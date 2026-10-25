# Project Description

I need to do some light measurement, reasonably high speed, from a display screen. I have some photo-transistors (and a few photo diodes, which IIRC, are a little slower in response) and a few Pi Picos. (I have other single board, esps, arduinos, etc, but I think the pico is the best for what I want - please correct me if wrong).

I tend to use PlatformIO and VSCode for this development, and I'm comfortable programming in the lowest level language we want to go for.

The thing is, I want to be able to get reliable luminance readings as fast as possible, and, hopefully, over several seconds of measurement. I know that means I need to cache the readings on the Pico probably, and dump them back to a laptop host (macos) after measurements... probably need to do some calibration too (I have other devices I can use, like the various X-Rite monitor calibrators, which I could -also- use but believe I don't have the speed there)

The goal, initially, is to make sure that, at a given refresh rate, a black/white flashing screen/checkerboard/vertical/horizontal stripes measures at (White-Black)/2 over a given integration area, but the solid White and Black measure at full values, there isn't lots of temporal roll off, etc.

Theoretically, we should see different results given different display technologies - LCD should be bad, LED (oLED or microLED) should probably be better, direct LED (like our LED walls) should be different, etc. 

I want to read this into Mathematica, as usual, for analysis, which I can do mostly by myself. Just looking for optimal aux hardware design here.

## Architecture & Hardware Justifications

### 1. Sensor Selection (Phototransistor vs. Photodiode)
- **Starting Point:** Phototransistor.
  - *Pros:* Internal bipolar gain ($\beta$) yields milliamp-range current directly into an ADC input across a simple load resistor ($R_L$), requiring zero active op-amp circuitry.
  - *Trade-off:* Base charge storage and Miller capacitance limit response times to ~2–15 µs (bandwidth ~50–150 kHz), dependent on $R_L$.
  - *Sizing:* Low $R_L$ (500 Ω – 2 kΩ) maximizes speed at the cost of dynamic range; high $R_L$ increases voltage swing but slows fall times.
- **Fallback / Alternative:** Photodiode.
  - Photodiodes are inherently much faster (sub-microsecond to nanosecond response, MHz/GHz bandwidth) but output microamps. If phototransistor roll-off muddies subpixel or microLED rise/fall measurements, we will swap to photodiode + Transimpedance Amplifier (TIA).

### 2. Microcontroller Selection: Raspberry Pi Pico (RP2040)
- **ADC Rate:** 12-bit SAR ADC capable of up to 500 kS/s (2 µs per sample) with hardware clock division (`adc_set_clkdiv`).
- **DMA + FIFO:** ADC conversions trigger hardware DMA directly into a circular or linear buffer in SRAM without CPU intervention or sample jitter.
- **Memory Buffer:** RP2040 has 264 KB SRAM. Dedicating ~200 KB to a 16-bit sample buffer holds 100,000 samples:
  - 5 seconds at 20 kS/s (50 µs sample interval, ~83 samples per 60 Hz frame).
  - 1 second at 100 kS/s (10 µs sample interval).
- **RP2040 ADC Linearity Note:** The RP2040 ADC has known errata (E9: DNL spikes at 512, 1024, etc.). Relative temporal waveform analysis is unhindered; precise photometric calibration can be corrected in Mathematica via LUT.

### 3. Debugging Hardware
- **Raspberry Pi Debug Probe:** Official CMSIS-DAP probe supported out of the box via PlatformIO (`debug_tool = cmsis-dap`, `upload_protocol = cmsis-dap`) using Raspberry Pi's OpenOCD (`tool-openocd-raspberrypi`). Provides SWD flashing/stepping and USB-UART serial bridge simultaneously.

## Important notes & Preferences

- I am an experienced programmer, 50 years of experience (go FORTRAN).
- I prefer using Wolfram Language outside the embedded languages.
- This IS NOT A PRODUCTION SOFTWARE PACKAGE: create code at the 'smart hacking about' level and DON'T OVER-STRESS about error conditions, etc.
- I'm macOS/Linux 99% of the time.
- I'm VSCode but was raised on emacs.
- I'm grumpy when you try too hard to satisfy your impressions about what you think I need.
- I prefer TOOLS over SOLUTIONS.
- We'll use PlatformIO if it makes the most sense.
- We'll use Pi Pico if it makes the most sense.

### Git & Repository Hygiene
- **Account / Ownership:** I am `flipphillips` on GitHub; stow/target most code under the `ritmps` organization/user.
- **Git-friendly:** Clean commits, keep builds and temporary artifacts out of git (`.gitignore`).
- **Git LFS:** Demanded for large files:
  - Mathematica notebooks (`*.nb`) containing large embedded outputs/rasters.
  - Captured raw measurement datasets (`*.bin`, `*.dat`, large `.csv`).
  - Images, plots, and figures (`*.png`, `*.jpg`, `*.pdf`).

## Howto: Physical Sampling Limits & Sensor Upgrade Paths

### 1. Phototransistor Physical Sampling Limits
* **The Physics Bottleneck:**
  - Phototransistors use bipolar multiplication ($\beta \approx 100\text{--}500$) to amplify photocurrent.
  - Base charge storage and the Miller effect ($C_{cb} \times \beta$) dictate transition speeds.
  - **Asymmetric response:** Rise time ($t_r$) is typically 2–8 µs, but **fall time ($t_f$) is 5–25 µs** because stored minority carriers have no base lead to drain through and must recombine internally.
  - **Bandwidth:** Typically 20 kHz – 100 kHz (dependent on load resistor $R_L$).
* **Sampling Ceiling:**
  - ADC rates beyond **50–100 kS/s** yield "empty" oversampling: you resolve the transistor's internal RC discharge curve rather than true display temporal transients.
* **What it CAN measure accurately:**
  - Display refresh rates and frame drops (60 Hz / 16.6 ms, 120 Hz / 8.3 ms, 240 Hz / 4.16 ms).
  - LCD pixel transitions (Gray-to-Gray typically 1 ms to 15 ms).
  - Backlight PWM dimming up to ~1–2 kHz.
  - Average luminance integration across frames.
* **What it CANNOT measure accurately:**
  - Microsecond-level subpixel pulse modulation (e.g., high-frequency OLED PWM >10 kHz).
  - True rise/fall edges of microLED or direct-LED wall strobe pulses (sensor will smooth the square edges into exponentials).

### 2. Moving to a Faster Photodiode
If edge analysis reveals sensor-limited roll-off, moving to a photodiode increases sensor bandwidth from ~50 kHz to >10 MHz (nanosecond response).

* **The Trade-Off (Why it needs active circuitry):**
  - Photodiodes output microamps ($I_p \approx 0.1\text{--}10\ \mu\text{A}$ at display luminance).
  - Pushing $10\ \mu\text{A}$ through a passive resistor into the ADC creates a dilemma:
    - Small $R_L$ (1 kΩ) $\to$ 10 mV swing (lost in ADC noise).
    - Large $R_L$ (100 kΩ) $\to$ 1 V swing, but stray capacitance ($C_{stray} \approx 10\text{ pF}$) forms an RC low-pass filter ($\tau = 1\ \mu\text{s}$), destroying the speed advantage.
* **What's Needed to Swap In a Photodiode:**
  1. **Active Circuit: Transimpedance Amplifier (TIA)**
     - Single rail-to-rail, high-gain-bandwidth op-amp (e.g., OPA350, OPA356, MCP6022, or AD8065) running from 3.3V.
     - Photodiode in **photoconductive mode** (reverse biased: cathode to 3.3V, anode to op-amp inverting input) minimizes junction capacitance ($C_j$).
     - Feedback resistor $R_f$ (e.g. 100 kΩ – 470 kΩ) sets gain ($V_{out} = I_p \times R_f$).
     - Small feedback capacitor $C_f$ (1–5 pF) across $R_f$ stabilizes the TIA loop against ringing.
  2. **Alternative (Pre-built Breakout):**
     - A dedicated photodiode + TIA sensor breakout module (or discrete TIA daughterboard).
  3. **Pico Hardware & Firmware Changes:**
     - **Firmware: Zero changes required.** The RP2040 ADC0 continues reading the 0–3.3V conditioned output.
     - **Sampling Rate:** You can safely crank the ADC up to the hardware ceiling of **500 kS/s** (2 µs per sample) knowing the front-end analog bandwidth is no longer the bottleneck.

