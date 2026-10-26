# photoquick

High-speed luminance measurement from display screens using a Raspberry Pi Pico (RP2040) and Wolfram Language / Mathematica.

---

## Hardware Hookup

### 1. Phototransistor (Phase 1 — Simplest, ~50 kHz limit)
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

### 2. Photodiode: Transimpedance Amplifier (Phase 2 — High Speed / MHz Bandwidth)

This is the recommended photodiode circuit. By holding the inverting input at virtual ground, the photodiode junction capacitance is never charged/discharged by the voltage swing, eliminating the RC bottleneck.

```
                       +----+--- [ C_f ] (1-5 pF) ---+----+
                       |    |                        |    |
                       |    +--- [ R_f ] (100k-470k) +    |
                       |                                  |
      Photodiode       |   |\                             |
        +---+          +---| - \                          |
    GND | A | (Anode)      |    \                         |
     |  |   |              |     >------------------------+---> GPIO 26 (ADC0, Pin 31)
    --- | K | (Cathode)+---| + /   (Rail-to-Rail Op-Amp,
        +---+          |   |/       e.g. MCP6001, OPA350)
                       |    |
                      GND  +3.3V (Pin 36) & GND (Pin 38)
```

* **How it works:**
  * **Photovoltaic / Zero-bias mode:** Anode to GND, Cathode to op-amp inverting input (`-`). Non-inverting input (`+`) to GND.
  * Photocurrent $I_p$ (flowing cathode $\to$ anode) is drawn from the op-amp output through $R_f$:
    $$V_{out} = I_p \times R_f$$
  * **Output swing:** Positive from ~15 mV (op-amp $V_{OL}$ in darkness) up to 3.0 V+ in bright screen light.
  * **$R_f$ selection:** $100\text{ k}\Omega$ yields $1.0\text{ V}$ per $10\ \mu\text{A}$; $470\text{ k}\Omega$ yields $4.7\text{ V}$ per $10\ \mu\text{A}$ (saturates near 3.3V).
  * **$C_f$ stabilization:** A small $1\text{--}5\text{ pF}$ capacitor in parallel with $R_f$ cancels the input capacitance pole and prevents op-amp ringing/oscillation.
  * **Op-Amp requirements:** Single-supply, Rail-to-Rail I/O (RRIO), low input bias current (FET/CMOS inputs), Gain Bandwidth Product (GBW) $\ge 5\text{ MHz}$ (e.g. Microchip MCP6001/MCP6022, TI OPA350/OPA356, Analog Devices AD8605).
  * **Decoupling:** Place a $0.1\ \mu\text{F}$ ceramic capacitor right between op-amp $V_{DD}$ and GND.

#### Alternative: All-in-One Breakout (OPT101)
If you have a TI OPT101 (monolithic photodiode + on-chip 1 MΩ TIA):
```
                 TI OPT101 (8-Pin DIP / Breakout)
                   +-----------------+
             -In --| 1             8 |-- +V  <-- +3.3V (Pin 36)
             -V  --| 2             7 |-- NC
            +In  --| 3    OPT101   6 |-- NC
             -V  --| 4             5 |-- Out --> GPIO 26 (ADC0, Pin 31)
                   +-----------------+
                    (Pins 2, 3, 4 tied to GND, Pin 38)
```

---

### 3. Photodiode: Passive Reverse-Biased (Quick & Dirty / No Op-Amp)

If you don't have an op-amp on hand and just want to test a photodiode immediately:

```
          +3.3V (Pin 36)
               |
             [ K ] Photodiode Cathode (stripe / flat / short lead)
             [ A ] Photodiode Anode
               |
 GPIO 26 <-----+  (ADC0, Pin 31)
               |
              [R_L] 20 kOhm - 100 kOhm
               |
              GND (Pin 33 or 38)
```
* **How it works:** Reverse-biases the diode with 3.3V. In darkness, voltage across $R_L$ is ~0V. In light, reverse photocurrent flows into $R_L$, pulling GPIO 26 up ($V = I_p \times R_L$).
* **Trade-off:** Without an op-amp virtual ground, $R_L$ forms an RC low-pass filter with diode junction capacitance ($C_j \approx 20\text{ pF}$) and ADC pin stray capacitance ($C_{stray} \approx 5\text{ pF}$). With $R_L = 100\text{ k}\Omega$, bandwidth is capped at $\sim 50\text{--}80\text{ kHz}$ — comparable to a phototransistor, but with a much smaller signal swing. Use the active TIA above for true microsecond speeds.

---

### EDA & Schematic Project Files (`hardware/`)

Project files for both EDA suites and standalone vector renders are located in [`hardware/`](file:///Users/fxpppr/GitHub/photoquick/hardware):

* **KiCad (v7 / v8):**
  * Project File: [`photoquick.kicad_pro`](file:///Users/fxpppr/GitHub/photoquick/hardware/kicad/photoquick.kicad_pro)
  * Circuit 1 (Phototransistor): [`phototransistor.kicad_sch`](file:///Users/fxpppr/GitHub/photoquick/hardware/kicad/phototransistor.kicad_sch) ([Rendered SVG](file:///Users/fxpppr/GitHub/photoquick/hardware/diagrams/kicad_phototransistor_schematic.svg))
  * Circuit 2 (Photodiode TIA): [`photodiode_tia.kicad_sch`](file:///Users/fxpppr/GitHub/photoquick/hardware/kicad/photodiode_tia.kicad_sch) ([Rendered SVG](file:///Users/fxpppr/GitHub/photoquick/hardware/diagrams/kicad_photodiode_tia_schematic.svg))
* **Fritzing:**
  * Circuit 1 (Phototransistor): [`phototransistor.fzz`](file:///Users/fxpppr/GitHub/photoquick/hardware/fritzing/phototransistor.fzz) / [`.fz XML`](file:///Users/fxpppr/GitHub/photoquick/hardware/fritzing/phototransistor.fz) ([Breadboard SVG](file:///Users/fxpppr/GitHub/photoquick/hardware/diagrams/fritzing_phototransistor_breadboard.svg))
  * Circuit 2 (Photodiode TIA): [`photodiode_tia.fzz`](file:///Users/fxpppr/GitHub/photoquick/hardware/fritzing/photodiode_tia.fzz) / [`.fz XML`](file:///Users/fxpppr/GitHub/photoquick/hardware/fritzing/photodiode_tia.fz) ([Breadboard SVG](file:///Users/fxpppr/GitHub/photoquick/hardware/diagrams/fritzing_photodiode_tia_breadboard.svg))

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

(* Analyze temporal luminance integration, rise/fall times, and frame-rate aliasing *)
analysis = PhotoquickFlickerAnalysis[blackData, whiteData, flickerData]
PhotoquickFlickerDashboard[analysis]

(* Generate frame-exact alternating Black/White stimulus videos (FullField, Checkerboard, Stripes) *)
PhotoquickGenerateStimulus["stimuli/fullfield_30fps.mp4", "FrameRate" -> 30, "Duration" -> 120.0, "Pattern" -> "FullField"]
```

---

## Archived Metrology Datasets & Temporal Integration Study (`captures/`)

Empirical `100 kS/s` measurements of temporal luminance integration ($\bar{L} \stackrel{?}{=} \frac{1}{2}(L_{\text{black}} + L_{\text{white}})$), liquid-crystal rise/fall asymmetry ($t_{\text{rise}} > t_{\text{fall}}$), and frame-rate vs. refresh-rate pulldown aliasing (`17`, `24`, `30`, and `60 fps` on a `120 Hz` ProMotion IPS LCD) are archived in [`captures/ipad_lcd_120hz/`](file:///Users/fxpppr/GitHub/photoquick/captures/ipad_lcd_120hz):

* **Full Technical Writeup & Mathematical Model:** [`captures/ipad_lcd_120hz/README.md`](file:///Users/fxpppr/GitHub/photoquick/captures/ipad_lcd_120hz/README.md)
* **Test Stimulus Suite (`17`, `24`, `30`, `60 fps` Full-Field & Coarse Checkerboards):** [`stimuli/`](file:///Users/fxpppr/GitHub/photoquick/stimuli)
* **Key Empirical Findings (iPad Pro `120 Hz` IPS LCD, $R_L = 9.4\text{ k}\Omega$):**
  * **Static Full-Field Baselines:** $L_{\text{white}} = 0.5812\text{ V}$ (`721.2` counts), $L_{\text{black}} = 0.0302\text{ V}$ (`37.4` counts), expected 50/50 temporal midpoint $= \mathbf{0.3057\text{ V}}$ (normalized `0.500`).
  * **Systematic Temporal Integration Deficit (`-17.5%` to `-20.3%`):** Across all four frame rates (`17`, `24`, `30`, `60 fps`), the cycle-bounded temporal mean $\bar{L}$ only reaches **`0.1941 – 0.2093 V`** (normalized **`0.297 – 0.325`**), driven by (1) dynamic White peak clamping (`0.405 – 0.415 V` vs. `0.5812 V` static) and (2) slower liquid-crystal rise time ($t_{\text{rise}} \approx 17.5\text{ ms}$) than fall time ($t_{\text{fall}} \approx 11.4\text{ ms}$), which pinches every White pulse `~6.8 – 7.3 ms` narrower than every Black trough.
  * **Direct Detection of `8:7` Pulldown Aliasing (`17 fps` on `120 Hz`):** At `17 fps` ($\frac{120}{17} = 7\frac{1}{17}$ refreshes/frame), 16 out of 17 frames hold for `7` refresh ticks (`54.70 ms` above midpoint) while every 17th frame holds for `8` refresh ticks (`63.07 ms`)—an exact **`+8.37 ms` (`1/120 Hz`)** pulldown leap ([`fullfield_17fps_dashboard.png`](file:///Users/fxpppr/GitHub/photoquick/captures/ipad_lcd_120hz/fullfield_17fps_dashboard.png)).
  * **High-Frequency Sawtooth Truncation (`60 fps`):** At `60 fps` (`16.67 ms`/frame $< t_{\text{rise}}$), the LCD never reaches a flat plateau, producing a pure sawtooth wave ([`fullfield_60fps_dashboard.png`](file:///Users/fxpppr/GitHub/photoquick/captures/ipad_lcd_120hz/fullfield_60fps_dashboard.png)).

---

## Photometric Calibration with Calibrite & ArgyllCMS (`spotread`)

The Calibrite device provides absolute DC luminance in $\text{cd/m}^2$ (nits) but has zero temporal speed. You can cross-calibrate the Pico in Mathematica using ArgyllCMS's [`spotread`](file:///opt/homebrew/bin/spotread):

1. **Take spot readings on static grey steps:**
   ```bash
   spotread -e -y l
   ```
2. **Build a LUT in Mathematica:**
   ```mathematica
   (* counts from Pico vs nits from spotread *)
   lut = Interpolation[{{countBlack, nitsBlack}, ..., {countWhite, nitsWhite}}, InterpolationOrder -> 1];

   (* Map dynamic ADC waveform to physical nits *)
   instantaneousNits = lut /@ data["RawCounts"];

   (* Numerical time-average over stimulus window *)
   picoMeanNits = Mean[instantaneousNits];
   ```
3. **Compare with Calibrite:** Place the Calibrite on the flashing/checkerboard stimulus to verify if the hardware optical integration matches `picoMeanNits` and $(L_{\text{white}} - L_{\text{black}})/2$.

