# High-Speed Optical Metrology of Display Flicker, Frame-Rate Aliasing, and Temporal Luminance Integration

## 1. Executive Summary & Core Finding

In vision science and psychophysics, a standard assumption derived from the **Talbot–Plateau Law** is that a display alternating rapidly with a 50% duty cycle between a dark state ($L_{\text{black}}$) and a bright state ($L_{\text{white}}$) produces a time-averaged physical luminance equal to the arithmetic midpoint:

$$L_{\text{expected}} = \frac{1}{2}\left(L_{\text{black}} + L_{\text{white}}\right)$$

Using the `photoquick` `100 kS/s` (`10 µs` resolution) Raspberry Pi Pico optical sensor (cross-calibrated against an X-Rite i1Display3 colorimeter at `0.292 µA/Lux`, loaded with $R_L = 9.4\text{ k}\Omega = 2 \times 4.7\text{ k}\Omega$ in series), we measured the real-time luminance waveforms $L(t)$ of an **iPad Pro (`120 Hz` ProMotion IPS LCD)** across static references and counter-phase / full-field flickering movies at **`17 fps`**, **`24 fps`**, **`30 fps`**, and **`60 fps`**.

**Core Empirical Result:**
Across every tested flicker frequency (`17`, `24`, `30`, and `60 fps`), the temporally integrated luminance $\bar{L} = \frac{1}{T}\int_0^T L(t)\,dt$ **never achieved the expected 50% gray midpoint** ($0.3057\text{ V}$, normalized `0.500`). Instead, the display consistently delivered a normalized mean of only **`0.297 – 0.325`** (`0.1941 – 0.2093 V`), representing a **`-17.5%` to `-20.3%` full-scale luminance deficit** (`~35%` lower physical light output than expected).

---

## 2. Mathematical Model: Why Temporal Integration Fails on Real LCDs

Suppose a stimulus commands alternating White and Black frames of nominal duration $T_f = \frac{1}{\text{fps}}$ (total cycle period $T = 2 T_f$). For the time-integrated luminance over one full cycle to equal the arithmetic mean $\frac{1}{2}(L_{\text{black}} + L_{\text{white}})$, two conditions must hold:

$$\bar{L} = \frac{1}{2 T_f} \left[ \int_0^{T_f} L_{\text{rise}}(t)\,dt + \int_{T_f}^{2T_f} L_{\text{fall}}(t)\,dt \right] \stackrel{?}{=} \frac{1}{2}\left(L_{\text{black}} + L_{\text{white}}\right)$$

If we model the rising transition (Black $\rightarrow$ White) with exponential time constant $\tau_r$ toward dynamic ceiling $L_W^* \le L_{\text{white}}$ and the falling transition (White $\rightarrow$ Black) with time constant $\tau_f$ toward $L_{\text{black}}$:

$$L_{\text{rise}}(t) = L_{\text{black}} + (L_W^* - L_{\text{black}})\left(1 - e^{-t/\tau_r}\right), \qquad L_{\text{fall}}(t') = L_{\text{black}} + (L_{\text{peak}} - L_{\text{black}}) e^{-t'/\tau_f}$$

Integrating over a full cycle yields two independent error terms that shift $\bar{L}$ away from $\frac{1}{2}(L_{\text{black}} + L_{\text{white}})$:

$$\Delta \bar{L} = \bar{L} - \frac{1}{2}(L_{\text{black}} + L_{\text{white}}) \approx \underbrace{-\frac{1}{2}\left(L_{\text{white}} - L_W^*\right)}_{\text{1. Peak White Clamping / Incomplete Settling}} \;-\; \underbrace{\frac{L_W^* - L_{\text{black}}}{2 T_f}\left(\tau_r - \tau_f\right)}_{\text{2. Rise/Fall Kinetic Asymmetry }(\tau_r > \tau_f)}$$

Both mechanisms are directly observed in our `100 kS/s` captures:

1. **Dynamic White Ceiling & Incomplete Frame Settling ($L_W^* < L_{\text{white}}$):**
   - Static full-screen White (`full_white.png`) produces **`0.5812 V`** (`721.2` ADC counts), and static full-screen Black (`full_black.png`) produces **`0.0302 V`** (`37.4` ADC counts).
   - During full-field alternating video playback, the White plateau clamps at **`0.405 – 0.415 V`** (`~70%` of static White). At `30 fps` (`33.3 ms`/frame) and `60 fps` (`16.7 ms`/frame), the liquid crystal is still rising when the frame ends, turning the `60 fps` waveform into a pure sawtooth/shark-fin wave with zero flat plateau.
2. **Asymmetric Liquid-Crystal Switching Kinetics ($t_{\text{rise}} > t_{\text{fall}}$):**
   - Measured `10%–90%` rise time (Black $\rightarrow$ White): **`16.5 – 17.5 ms`**
   - Measured `90%–10%` fall time (White $\rightarrow$ Black): **`11.4 ms`** (`1.53×` faster fall than rise)
   - Because turning the pixel from Black to White takes `~6 ms` longer than relaxing from White to Black, **every White frame is pinched narrower by `~6.8 – 7.3 ms` compared to every Black frame** at `17`, `24`, and `30 fps`.

---

## 3. Quantitative Summary of Captured Datasets

All raw Wolfram Data Exchange (`.wdx`) capture files (`98,304` samples @ `100,000 Hz`, `10 µs` resolution) and diagnostic plots are archived in this directory (`captures/ipad_lcd_120hz/`).

| Dataset File | Condition | Frame Period ($T_f$) | `120 Hz` Refresh Cadence | Measured Rate | White Hold Duration | Black Hold Duration | Measured Mean ($\bar{L}$) | Normalized Mean (Expected `0.500`) | Integration Error (% of Span) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [`full_white_ref.wdx`](./full_white_ref.wdx) | Static Full White | $\infty$ | Continuous `120 Hz` | — | — | — | **`0.5812 V`** | `1.000` | — |
| [`full_black_ref.wdx`](./full_black_ref.wdx) | Static Full Black | $\infty$ | Continuous `120 Hz` | — | — | — | **`0.0302 V`** | `0.000` | — |
| [`fullfield_17fps.wdx`](./fullfield_17fps.wdx) | `17 fps` Full-Field | `58.82 ms` | **`7` or `8` ticks (`8:7` alias)** | `16.96 fps` (`8.48 Hz`) | `54.7 ms` *(+`63.1 ms` leap)* | `62.0 ms` | **`0.2066 V`** | **`0.320`** | **`-17.97%`** |
| [`fullfield_24fps.wdx`](./fullfield_24fps.wdx) | `24 fps` Full-Field | `41.67 ms` | **`5` ticks** *(1 slip on #4)* | `23.98 fps` (`11.99 Hz`) | `38.3 ms` | `45.1 ms` | **`0.1941 V`** | **`0.297`** | **`-20.25%`** |
| [`fullfield_30fps.wdx`](./fullfield_30fps.wdx) | `30 fps` Full-Field | `33.33 ms` | **`4` ticks** | `29.98 fps` (`14.99 Hz`) | `~29.9 ms` | `~36.8 ms` | **`0.1950 V`** | **`0.299`** | **`-20.08%`** |
| [`fullfield_60fps.wdx`](./fullfield_60fps.wdx) | `60 fps` Full-Field | `16.67 ms` | **`2` ticks** (Sawtooth) | `59.98 fps` (`29.99 Hz`) | `15.9 ms` | `17.4 ms` | **`0.2093 V`** | **`0.325`** | **`-17.49%`** |
| [`white_30fps_ref.wdx`](./white_30fps_ref.wdx) | Checkerboard White Tile | $\infty$ | Continuous `120 Hz` | — | — | — | **`0.5608 V`** | — | *(Lateral dark-tile loss: `-20.4 mV`)* |
| [`black_30fps_ref.wdx`](./black_30fps_ref.wdx) | Checkerboard Black Tile | $\infty$ | Continuous `120 Hz` | — | — | — | **`0.0735 V`** | — | *(Lateral white-tile bleed: `+43.3 mV`)* |
| [`flicker_30fps.wdx`](./flicker_30fps.wdx) | `30 fps` Checkerboard | `33.33 ms` | Counter-phase spatial cancel | `30.00 fps` (`15.00 Hz`) | — | — | **`0.2445 V`** | **`0.351`** | **`-14.92%`** |

---

## 4. Frame-Rate vs. Refresh-Rate Temporal Aliasing (`17 fps` on `120 Hz`)

Because the iPad Pro panel refreshes at **`120.0 Hz`** (`8.333 ms` per refresh tick, directly visible as an `8.33 ms` impulse comb in [`full_black_ref_zoom50ms.png`](./full_black_ref_zoom50ms.png) and in the dark troughs of all flicker waveforms):
- **`60 fps` (`120 / 60 = 2`):** Every frame holds for exactly `2` refresh ticks (`16.67 ms`).
- **`30 fps` (`120 / 30 = 4`):** Every frame holds for exactly `4` refresh ticks (`33.33 ms`).
- **`24 fps` (`120 / 24 = 5`):** Every frame holds for `5` refresh ticks (`41.67 ms`), avoiding standard `60 Hz` `3:2` pulldown judder (though our `100 kS/s` capture caught a single `4.15 ms` compositor phase slip on Cycle #4 in [`fullfield_24fps_dashboard.png`](./fullfield_24fps_dashboard.png)).
- **`17 fps` (`120 / 17 = 7.0588`):** Since $120 = 7 \times 17 + 1$, `17 fps` cannot divide into `120 Hz`. The display must hold 16 out of 17 frames for **`7` refreshes (`58.33 ms`)** and every 17th frame for **`8` refreshes (`66.67 ms`)**. In [`fullfield_17fps_dashboard.png`](./fullfield_17fps_dashboard.png), White frames 1, 3, 4, 5, 6, 7, 8 hold for **`54.70 ± 0.04 ms`**, while **White Frame #2 leaps to `63.07 ms`**—an exact **`+8.37 ms` (`1/120 Hz`)** pulldown alias quantum.

---

## 5. Spatial Cross-Talk in Uncollimated Checkerboard Measurements

Comparing the coarse `4 × 3` checkerboard (`480 × 360 px` tiles) against the full-field stimuli revealed an important optical metrology consideration for bare phototransistors (which have a $\pm 25^\circ$ acceptance cone):
- **Static Black Floor:** `30.2 mV` (Full-Screen Black) vs. `73.5 mV` (Checkerboard Black square surrounded by White neighbors)—a `+43.3 mV` (`2.4×`) increase due to wide-angle acceptance and lateral light piping inside the cover glass.
- **Counter-Phase Cancellation:** When a coarse checkerboard counter-phase flickers (`flicker_30fps.wdx`), the square under the sensor and its immediate 4-connected neighbors oscillate $180^\circ$ out of phase, cancelling >90% of the AC modulation at an uncollimated sensor unless a matte-black baffle tube / field-stop aperture or imaging lens restricts the sensor's field of view to a single tile.
