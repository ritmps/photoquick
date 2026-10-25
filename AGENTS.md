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
