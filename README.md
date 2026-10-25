# photoquick

High-speed luminance measurement from display screens using a Raspberry Pi Pico (RP2040) and Wolfram Language / Mathematica.

---

## Hardware Hookup

### 1. Phototransistor (Phase 1)
```
          +3.3V (Pin 36)
               |
             [ C ] Phototransistor
             [ E ]
               |
 GPIO 26 <-----+  (ADC0, Pin 31)
               |
              [R_L] 500 Ohm - 2 kOhm (e.g. 1 kOhm)
               |
              GND (Pin 33 or 38)
```
* **$R_L$ Sizing:**
  * Lower $R_L$ (500 Ω – 1 kΩ): Faster edge response, smaller voltage swing.
  * Higher $R_L$ (2 kΩ – 10 kΩ): Larger voltage swing, slower fall times.

---

## Physical Sampling Limits: Phototransistor vs. Photodiode

### Phototransistor Limits
* **Bandwidth:** ~20 kHz – 100 kHz.
* **Fall-time asymmetry:** Rise time is typically 2–8 µs, but **fall time is 5–25 µs** because trapped minority carriers in the floating base must recombine internally.
* **Sampling Ceiling:** Sampling above **50–100 kS/s** oversamples the transistor's internal RC decay curve rather than optical screen physics.
* **Good for:** 60/120/240 Hz refresh timing, frame drops, LCD Gray-to-Gray response times (1–15 ms), PWM dimming up to ~1–2 kHz.
* **Not suitable for:** Subpixel OLED/microLED PWM at >10 kHz or true nanosecond edge transitions.

### Moving to a Faster Photodiode
Photodiodes provide **MHz to GHz bandwidth** (nanosecond rise/fall), but produce microamps ($0.1\text{--}10\ \mu\text{A}$ at typical display illuminance).
* **Why passive resistors won't work:** A small resistor yields a signal lost in ADC noise; a large resistor creates an RC low-pass filter with cable/pin stray capacitance, negating the speed.
* **Required upgrade:** A **Transimpedance Amplifier (TIA)** using a high-gain-bandwidth, rail-to-rail op-amp (e.g. OPA350, OPA356, MCP6022, AD8065) or an integrated photodiode+TIA breakout.
  * Reverse-bias the photodiode (photoconductive mode) into the op-amp inverting input.
  * $R_f$ (100 kΩ – 470 kΩ) sets gain ($V_{out} = I_p \times R_f$).
  * Small capacitor $C_f$ (1–5 pF) across $R_f$ prevents ringing.
* **Firmware changes:** **None.** The RP2040 ADC0 pin still samples 0–3.3V. You can immediately increase the sample rate to the hardware maximum of **500 kS/s** (2 µs resolution).

---

## Firmware & Debugging (PlatformIO)

### Build & Upload
```bash
# Standard USB drag-and-drop / picotool upload
pio run -e pico -t upload

# Upload via Raspberry Pi Debug Probe (CMSIS-DAP over SWD)
pio run -e pico_probe -t upload
```

### Raspberry Pi Debug Probe Connections
* **Debug port (D):** Connect `GND`, `SWCLK`, and `SWDIO` to the 3-pin SWD header on the bottom edge of the Pico.
* **UART port (U):** Optional serial connection to Pico `GP0 (TX)` and `GP1 (RX)`.
* **VSCode Debugging:** Press **F5** to start an interactive CMSIS-DAP debugging session with hardware breakpoints and RP2040 register inspection (`rp2040.svd`).

### Firmware Serial Commands (115200 baud)
* `c` : Capture 100k samples via DMA and dump binary buffer.
* `m` : Live 10 Hz monitor mode (prints raw ADC counts and volts for optical alignment).
* `d` : Dump current buffer as ASCII CSV lines.
* `1` : Set rate to 20 kS/s (5.0 s capture window).
* `2` : Set rate to 50 kS/s (2.0 s capture window).
* `3` : Set rate to 100 kS/s (1.0 s capture window) [default].
* `4` : Set rate to 500 kS/s (0.2 s capture window, max ADC limit).
* `?` : Display help menu.

---

## Wolfram Language / Mathematica Usage

```mathematica
Get["photoquick.wl"]

(* Automatically detects /dev/cu.usbmodem*, triggers capture, and reads buffer *)
data = PhotoquickCapture[]

(* Or manually specify device *)
(* data = PhotoquickCapture["/dev/cu.usbmodem14101"] *)

(* Inspect metadata *)
data["SampleRate"]
data["Duration"]

(* Plot voltage vs time *)
PhotoquickPlot[data]
```
