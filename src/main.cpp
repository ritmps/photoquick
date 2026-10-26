/*
 * photoquick: High-speed luminance measurement using RP2040 ADC + DMA.
 *
 * Sensor hookup:
 *   Phototransistor Collector -> 3V3 (Pico pin 36)
 *   Phototransistor Emitter   -> GPIO 26 / ADC0 (Pico pin 31)
 *   Load resistor (500R-2k)   -> between GPIO 26 and GND (Pico pin 33/38)
 *
 * Serial commands (115200 baud):
 *   '?' : Print status & command menu
 *   'c' : Trigger capture into SRAM, then dump binary over USB
 *   'd' : Dump last captured buffer as CSV (ASCII counts)
 *   'b' : Dump last captured buffer as raw binary (uint16_t little-endian)
 *   'm' : Real-time monitor mode (stream continuous ASCII readings, send any key to stop)
 *   '1' : Set rate to 20 kS/s (5.0s buffer at 100k samples)
 *   '2' : Set rate to 50 kS/s (2.0s buffer at 100k samples)
 *   '3' : Set rate to 100 kS/s (1.0s buffer at 100k samples) [default]
 *   '4' : Set rate to 500 kS/s (0.2s buffer at 100k samples, max ADC speed)
 */

#include <Arduino.h>
#include "hardware/adc.h"
#include "hardware/dma.h"

#define ADC_PIN 26
#define ADC_CHAN 0

// 100,000 samples * 2 bytes = 200 KB (fits comfortably in RP2040's 264 KB SRAM)
#define NUM_SAMPLES 100000

static uint16_t sample_buffer[NUM_SAMPLES];
static int dma_chan = -1;
static uint32_t current_rate_hz = 100000;

void set_adc_sample_rate(uint32_t rate_hz) {
    if (rate_hz > 500000) rate_hz = 500000;
    if (rate_hz < 1000) rate_hz = 1000;
    current_rate_hz = rate_hz;

    // RP2040 ADC clock is 48 MHz.
    // Conversions take 96 cycles base, so clkdiv formula is:
    // f_sample = 48,000,000 / (1 + clkdiv)
    // clkdiv = (48,000,000 / f_sample) - 1
    float clkdiv = (48000000.0f / (float)rate_hz) - 1.0f;
    if (clkdiv < 0.0f) clkdiv = 0.0f;
    adc_set_clkdiv(clkdiv);
}

void init_adc_dma() {
    adc_init();
    adc_gpio_init(ADC_PIN);
    adc_select_input(ADC_CHAN);

    // Setup ADC FIFO:
    // threshold = 1 (request DMA on every sample)
    // dreq_en = true
    // err_in_fifo = false
    // byte_shift = false (12-bit sample in 16-bit word)
    adc_fifo_setup(true, true, 1, false, false);

    set_adc_sample_rate(current_rate_hz);

    dma_chan = dma_claim_unused_channel(true);
}

void run_capture() {
    // Drain any stale FIFO entries
    adc_fifo_drain();

    dma_channel_config cfg = dma_channel_get_default_config(dma_chan);
    channel_config_set_transfer_data_size(&cfg, DMA_SIZE_16);
    channel_config_set_read_increment(&cfg, false);
    channel_config_set_write_increment(&cfg, true);
    channel_config_set_dreq(&cfg, DREQ_ADC);

    dma_channel_configure(
        dma_chan,
        &cfg,
        sample_buffer,        // dest
        &adc_hw->fifo,        // src
        NUM_SAMPLES,          // count
        true                  // start DMA
    );

    // Start ADC free-running conversions
    adc_run(true);

    // Wait for DMA completion
    dma_channel_wait_for_finish_blocking(dma_chan);

    // Stop ADC
    adc_run(false);
    adc_fifo_drain();
}

void dump_binary() {
    // Send 8-byte header: MAGIC ("PQ01"), uint32 sample_rate
    const char magic[4] = {'P', 'Q', '0', '1'};
    Serial.write((const uint8_t*)magic, 4);
    uint32_t rate = current_rate_hz;
    Serial.write((const uint8_t*)&rate, 4);

    // Stream raw buffer in 4 KB chunks with brief pacing so macOS XNU tty buffer (64 KB TTYHOG) never drops bytes
    const uint8_t* ptr = (const uint8_t*)sample_buffer;
    size_t remaining = NUM_SAMPLES * sizeof(uint16_t);
    const size_t chunk_size = 4096;
    while (remaining > 0) {
        size_t to_write = (remaining < chunk_size) ? remaining : chunk_size;
        Serial.write(ptr, to_write);
        ptr += to_write;
        remaining -= to_write;
        delay(2);
    }
    Serial.flush();
}

void dump_csv() {
    Serial.println(F("# photoquick dump"));
    Serial.print(F("# Sample rate: "));
    Serial.print(current_rate_hz);
    Serial.println(F(" Hz"));
    Serial.print(F("# Samples: "));
    Serial.println(NUM_SAMPLES);
    for (size_t i = 0; i < NUM_SAMPLES; i++) {
        Serial.println(sample_buffer[i]);
    }
}

void monitor_mode() {
    Serial.println(F("Live monitor mode. Press any key to stop..."));
    adc_fifo_setup(false, false, 0, false, false);
    adc_run(false);

    while (!Serial.available()) {
        uint16_t val = adc_read();
        float volts = (val * 3.3f) / 4095.0f;
        Serial.print(F("ADC: "));
        Serial.print(val);
        Serial.print(F(" ("));
        Serial.print(volts, 3);
        Serial.println(F(" V)"));
        delay(100);
    }
    while (Serial.available()) Serial.read();

    // Restore FIFO for DMA
    adc_fifo_setup(true, true, 1, false, false);
    set_adc_sample_rate(current_rate_hz);
}

void print_help() {
    Serial.println();
    Serial.println(F("=== photoquick RP2040 Light Sensor ==="));
    Serial.print(F("Buffer: "));
    Serial.print(NUM_SAMPLES);
    Serial.print(F(" samples | Current Rate: "));
    Serial.print(current_rate_hz);
    Serial.print(F(" Hz ("));
    Serial.print((float)NUM_SAMPLES / (float)current_rate_hz, 2);
    Serial.println(F(" s)"));
    Serial.println(F("Commands:"));
    Serial.println(F("  c : Capture buffer and dump binary"));
    Serial.println(F("  b : Dump last buffer (binary)"));
    Serial.println(F("  d : Dump last buffer (CSV text)"));
    Serial.println(F("  m : Real-time live monitor"));
    Serial.println(F("  1 : Set 20 kS/s  (5.0 s capture)"));
    Serial.println(F("  2 : Set 50 kS/s  (2.0 s capture)"));
    Serial.println(F("  3 : Set 100 kS/s (1.0 s capture)"));
    Serial.println(F("  4 : Set 500 kS/s (0.2 s capture)"));
    Serial.println(F("  ? : Print this help"));
}

void setup() {
    Serial.begin(115200);
    init_adc_dma();
}

void loop() {
    if (Serial.available()) {
        char cmd = Serial.read();
        switch (cmd) {
            case 'c':
                run_capture();
                dump_binary();
                break;
            case 'b':
                dump_binary();
                break;
            case 'd':
                dump_csv();
                break;
            case 'm':
                monitor_mode();
                break;
            case '1':
                set_adc_sample_rate(20000);
                print_help();
                break;
            case '2':
                set_adc_sample_rate(50000);
                print_help();
                break;
            case '3':
                set_adc_sample_rate(100000);
                print_help();
                break;
            case '4':
                set_adc_sample_rate(500000);
                print_help();
                break;
            case '?':
            case 'h':
                print_help();
                break;
            default:
                break;
        }
    }
}
