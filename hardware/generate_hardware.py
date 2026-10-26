#!/usr/bin/env python3
"""
Generate KiCad and Fritzing input files + standalone SVG visualizations
for Photoquick's sensor circuits:
1. Phototransistor (Phase 1)
2. Photodiode + TIA (Phase 2)
"""

import os
import zipfile
import uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KICAD_DIR = os.path.join(BASE_DIR, "kicad")
FRITZING_DIR = os.path.join(BASE_DIR, "fritzing")
DIAGRAMS_DIR = os.path.join(BASE_DIR, "diagrams")

for d in [KICAD_DIR, FRITZING_DIR, DIAGRAMS_DIR]:
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. KiCad v7/v8 Project & Schematics
# ---------------------------------------------------------------------------

KICAD_PRO = """{
  "meta": {
    "filename": "photoquick.kicad_pro",
    "version": 1
  },
  "project": {
    "files": []
  },
  "schematic": {
    "annotate_start_num": 1,
    "drawing": {
      "default_line_thickness": 0.1524,
      "default_text_size": 1.27
    }
  }
}
"""

def generate_kicad_phototransistor():
    u_sch = str(uuid.uuid4())
    u_pico = str(uuid.uuid4())
    u_trans = str(uuid.uuid4())
    u_r1 = str(uuid.uuid4())
    u_pwr1 = str(uuid.uuid4())
    u_gnd1 = str(uuid.uuid4())
    
    return f"""(kicad_sch (version 20231120) (generator "eeschema") (generator_version "8.0")
  (uuid "{u_sch}")
  (paper "A4")
  (title_block
    (title "Photoquick - Phototransistor Detector (Phase 1)")
    (date "2026-10-25")
    (rev "1.0")
    (company "ritmps / photoquick")
    (comment 1 "High-Speed Optical Luminance Measurement")
  )

  (lib_symbols
    (symbol "Device:Q_Photo_NPN" (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "Q" (at 2.54 2.54 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Phototransistor_NPN" (at 2.54 -2.54 0) (effects (font (size 1.27 1.27))))
      (symbol "Q_Photo_NPN_0_1"
        (circle (center 0 0) (radius 2.8) (stroke (width 0.254) (type solid)) (fill (type none)))
        (polyline (pts (xy 0 1.5) (xy 0 0.5) (xy 1.5 2)) (stroke (width 0.254) (type solid)) (fill (type none)))
        (polyline (pts (xy 0 -1.5) (xy 0 -0.5) (xy 1.5 -2)) (stroke (width 0.254) (type solid)) (fill (type none)))
        (pin passive line (at 2.54 3.81 270) (length 1.81) (name "C" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 2.54 -3.81 90) (length 1.81) (name "E" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "Device:R" (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "R" (at 2.0 0 0) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (at -2.0 0 0) (effects (font (size 1.27 1.27))))
      (symbol "R_0_1"
        (rectangle (start -1.0 2.54) (end 1.0 -2.54) (stroke (width 0.254) (type solid)) (fill (type none)))
        (pin passive line (at 0 3.81 270) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 0 -3.81 90) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "MCU_RaspberryPi_Pico:Pico_Header" (pin_names (offset 1.0)) (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 25.4 0) (effects (font (size 1.27 1.27))))
      (property "Value" "RP2040_Pico" (at 0 -25.4 0) (effects (font (size 1.27 1.27))))
      (symbol "Pico_0_1"
        (rectangle (start -15.24 22.86) (end 15.24 -22.86) (stroke (width 0.254) (type solid)) (fill (type none)))
        (pin power_out line (at -17.78 15.24 0) (length 2.54) (name "3V3_OUT (Pin 36)" (effects (font (size 1.27 1.27)))) (number "36" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at -17.78 -15.24 0) (length 2.54) (name "GND (Pin 38)" (effects (font (size 1.27 1.27)))) (number "38" (effects (font (size 1.27 1.27)))))
        (pin input line (at -17.78 0 0) (length 2.54) (name "GPIO26_ADC0 (Pin 31)" (effects (font (size 1.27 1.27)))) (number "31" (effects (font (size 1.27 1.27)))))
      )
    )
  )

  (symbol (lib_id "MCU_RaspberryPi_Pico:Pico_Header") (at 190.5 101.6 0) (unit 1)
    (uuid "{u_pico}")
    (property "Reference" "U1" (at 190.5 73.66 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Raspberry Pi Pico" (at 190.5 129.54 0) (effects (font (size 1.27 1.27))))
  )

  (symbol (lib_id "Device:Q_Photo_NPN") (at 114.3 88.9 0) (unit 1)
    (uuid "{u_trans}")
    (property "Reference" "Q1" (at 121.92 86.36 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Phototransistor (e.g. TEPT5600 / L-53P3C)" (at 121.92 88.9 0) (effects (font (size 1.27 1.27))))
  )

  (symbol (lib_id "Device:R") (at 114.3 114.3 0) (unit 1)
    (uuid "{u_r1}")
    (property "Reference" "R1" (at 120.65 113.03 0) (effects (font (size 1.27 1.27))))
    (property "Value" "1k (500R - 2k)" (at 120.65 115.57 0) (effects (font (size 1.27 1.27))))
  )

  (wire (pts (xy 114.3 85.09) (xy 114.3 76.2)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 114.3 76.2) (xy 172.72 76.2)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 172.72 76.2) (xy 172.72 86.36)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))

  (wire (pts (xy 114.3 92.71) (xy 114.3 101.6)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 114.3 101.6) (xy 114.3 110.49)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 114.3 101.6) (xy 172.72 101.6)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))

  (wire (pts (xy 114.3 118.11) (xy 114.3 127.0)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 114.3 127.0) (xy 172.72 127.0)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 172.72 127.0) (xy 172.72 116.84)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))

  (junction (at 114.3 101.6) (diameter 1.0) (color 0 0 0 0) (uuid "{uuid.uuid4()}"))

  (text "Signal: 0 - 3.3V into Pico ADC0\\nBandwidth: ~50-100 kHz\\nt_r ~3us, t_f ~15us" (at 114.3 140.0 0) (effects (font (size 1.5 1.5))))
)
"""

def generate_kicad_photodiode_tia():
    u_sch = str(uuid.uuid4())
    u_pico = str(uuid.uuid4())
    u_d1 = str(uuid.uuid4())
    u_opamp = str(uuid.uuid4())
    u_rf = str(uuid.uuid4())
    u_cf = str(uuid.uuid4())
    u_cdec = str(uuid.uuid4())

    return f"""(kicad_sch (version 20231120) (generator "eeschema") (generator_version "8.0")
  (uuid "{u_sch}")
  (paper "A4")
  (title_block
    (title "Photoquick - Photodiode Transimpedance Amplifier (Phase 2)")
    (date "2026-10-25")
    (rev "1.0")
    (company "ritmps / photoquick")
    (comment 1 "High-Speed Transimpedance Amplifier (TIA)")
  )

  (lib_symbols
    (symbol "Device:D_Photo" (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "D" (at 2.0 0 0) (effects (font (size 1.27 1.27))))
      (property "Value" "Photodiode" (at -2.0 0 0) (effects (font (size 1.27 1.27))))
      (symbol "D_Photo_0_1"
        (polyline (pts (xy -1.27 -1.27) (xy 1.27 0) (xy -1.27 1.27) (xy -1.27 -1.27)) (stroke (width 0.254) (type solid)) (fill (type none)))
        (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27)) (stroke (width 0.254) (type solid)) (fill (type none)))
        (pin passive line (at -3.81 0 0) (length 2.54) (name "A" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 3.81 0 180) (length 2.54) (name "K" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "Amplifier_Operational:OpAmp_Single" (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 5.08 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "MCP6001_OPA350" (at 5.08 -5.08 0) (effects (font (size 1.27 1.27))))
      (symbol "OpAmp_0_1"
        (polyline (pts (xy -5.08 5.08) (xy 5.08 0) (xy -5.08 -5.08) (xy -5.08 5.08)) (stroke (width 0.254) (type solid)) (fill (type none)))
        (pin input line (at -7.62 2.54 0) (length 2.54) (name "-" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
        (pin input line (at -7.62 -2.54 0) (length 2.54) (name "+" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
        (pin output line (at 7.62 0 180) (length 2.54) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at 0 6.35 270) (length 3.81) (name "V+" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at 0 -6.35 90) (length 3.81) (name "V-" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "Device:R" (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "R" (at 2.0 0 0) (effects (font (size 1.27 1.27))))
      (property "Value" "R" (at -2.0 0 0) (effects (font (size 1.27 1.27))))
      (symbol "R_0_1"
        (rectangle (start -2.54 1.0) (end 2.54 -1.0) (stroke (width 0.254) (type solid)) (fill (type none)))
        (pin passive line (at -3.81 0 0) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 3.81 0 180) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "Device:C" (pin_names (offset 0)) (in_bom yes) (on_board yes)
      (property "Reference" "C" (at 2.0 0 0) (effects (font (size 1.27 1.27))))
      (property "Value" "C" (at -2.0 0 0) (effects (font (size 1.27 1.27))))
      (symbol "C_0_1"
        (polyline (pts (xy -0.635 1.5) (xy -0.635 -1.5)) (stroke (width 0.254) (type solid)) (fill (type none)))
        (polyline (pts (xy 0.635 1.5) (xy 0.635 -1.5)) (stroke (width 0.254) (type solid)) (fill (type none)))
        (pin passive line (at -2.54 0 0) (length 1.905) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 2.54 0 180) (length 1.905) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      )
    )
    (symbol "MCU_RaspberryPi_Pico:Pico_Header" (pin_names (offset 1.0)) (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 25.4 0) (effects (font (size 1.27 1.27))))
      (property "Value" "RP2040_Pico" (at 0 -25.4 0) (effects (font (size 1.27 1.27))))
      (symbol "Pico_0_1"
        (rectangle (start -15.24 22.86) (end 15.24 -22.86) (stroke (width 0.254) (type solid)) (fill (type none)))
        (pin power_out line (at -17.78 15.24 0) (length 2.54) (name "3V3_OUT (Pin 36)" (effects (font (size 1.27 1.27)))) (number "36" (effects (font (size 1.27 1.27)))))
        (pin power_in line (at -17.78 -15.24 0) (length 2.54) (name "GND (Pin 38)" (effects (font (size 1.27 1.27)))) (number "38" (effects (font (size 1.27 1.27)))))
        (pin input line (at -17.78 0 0) (length 2.54) (name "GPIO26_ADC0 (Pin 31)" (effects (font (size 1.27 1.27)))) (number "31" (effects (font (size 1.27 1.27)))))
      )
    )
  )

  (symbol (lib_id "MCU_RaspberryPi_Pico:Pico_Header") (at 200.0 101.6 0) (unit 1)
    (uuid "{u_pico}")
    (property "Reference" "U1" (at 200.0 73.66 0) (effects (font (size 1.27 1.27))))
    (property "Value" "Raspberry Pi Pico" (at 200.0 129.54 0) (effects (font (size 1.27 1.27))))
  )

  (symbol (lib_id "Amplifier_Operational:OpAmp_Single") (at 130.0 101.6 0) (unit 1)
    (uuid "{u_opamp}")
    (property "Reference" "U2" (at 130.0 88.9 0) (effects (font (size 1.27 1.27))))
    (property "Value" "MCP6001 / OPA350" (at 130.0 114.3 0) (effects (font (size 1.27 1.27))))
  )

  (symbol (lib_id "Device:D_Photo") (at 95.0 99.06 0) (unit 1)
    (uuid "{u_d1}")
    (property "Reference" "D1" (at 95.0 92.0 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BPW34 / TEMD5010" (at 95.0 106.0 0) (effects (font (size 1.27 1.27))))
  )

  (symbol (lib_id "Device:R") (at 130.0 80.0 0) (unit 1)
    (uuid "{u_rf}")
    (property "Reference" "Rf" (at 130.0 75.0 0) (effects (font (size 1.27 1.27))))
    (property "Value" "100k - 470k" (at 130.0 85.0 0) (effects (font (size 1.27 1.27))))
  )

  (symbol (lib_id "Device:C") (at 130.0 68.0 0) (unit 1)
    (uuid "{u_cf}")
    (property "Reference" "Cf" (at 130.0 63.0 0) (effects (font (size 1.27 1.27))))
    (property "Value" "2.2pF (1-5pF)" (at 130.0 73.0 0) (effects (font (size 1.27 1.27))))
  )

  (wire (pts (xy 98.81 99.06) (xy 122.38 99.06)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 110.0 99.06) (xy 110.0 80.0)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 110.0 80.0) (xy 126.19 80.0)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 110.0 80.0) (xy 110.0 68.0)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 110.0 68.0) (xy 127.46 68.0)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))

  (wire (pts (xy 137.62 101.6) (xy 155.0 101.6)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 155.0 101.6) (xy 155.0 80.0)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 133.81 80.0) (xy 155.0 80.0)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 155.0 80.0) (xy 155.0 68.0)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 132.54 68.0) (xy 155.0 68.0)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))

  (wire (pts (xy 155.0 101.6) (xy 182.22 101.6)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))

  (wire (pts (xy 91.19 99.06) (xy 85.0 99.06)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 85.0 99.06) (xy 85.0 116.84)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 122.38 104.14) (xy 120.0 104.14)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 120.0 104.14) (xy 120.0 116.84)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 130.0 107.95) (xy 130.0 116.84)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 85.0 116.84) (xy 182.22 116.84)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))

  (wire (pts (xy 130.0 95.25) (xy 130.0 86.36)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))
  (wire (pts (xy 130.0 86.36) (xy 182.22 86.36)) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))

  (junction (at 110.0 99.06) (diameter 1.0) (color 0 0 0 0) (uuid "{uuid.uuid4()}"))
  (junction (at 110.0 80.0) (diameter 1.0) (color 0 0 0 0) (uuid "{uuid.uuid4()}"))
  (junction (at 155.0 101.6) (diameter 1.0) (color 0 0 0 0) (uuid "{uuid.uuid4()}"))
  (junction (at 155.0 80.0) (diameter 1.0) (color 0 0 0 0) (uuid "{uuid.uuid4()}"))
  (junction (at 120.0 116.84) (diameter 1.0) (color 0 0 0 0) (uuid "{uuid.uuid4()}"))
  (junction (at 130.0 116.84) (diameter 1.0) (color 0 0 0 0) (uuid "{uuid.uuid4()}"))

  (text "High-Speed Transimpedance Amplifier\\nVout = Ip * Rf (Active High 0 - 3.3V)\\nBandwidth > 1 MHz (Allows full 500 kS/s sampling)" (at 90.0 135.0 0) (effects (font (size 1.5 1.5))))
)
"""

# ---------------------------------------------------------------------------
# 2. Fritzing Sketch XML (.fz) & Bundled (.fzz)
# ---------------------------------------------------------------------------

def generate_fritzing_phototransistor():
    return """<?xml version="1.0" encoding="UTF-8"?>
<module fritzingVersion="0.9.10" icon="photoquick_pt.png">
    <title>Photoquick - Phototransistor Detector</title>
    <label>PQ-PT</label>
    <date>2026-10-25</date>
    <author>ritmps / photoquick</author>
    <description>Circuit 1: RP2040 Pico + Phototransistor + Load Resistor</description>
    <views>
        <view name="breadboardView" zoom="1.0" x="0" y="0"/>
        <view name="schematicView" zoom="1.0" x="0" y="0"/>
        <view name="pcbView" zoom="1.0" x="0" y="0"/>
    </views>
    <instances>
        <!-- Raspberry Pi Pico -->
        <instance moduleIdRef="Raspberry-Pi-Pico_breadboard" modelIndex="1001" path="">
            <title>Pico1</title>
            <property name="family" value="microcontroller"/>
            <views>
                <breadboardView layer="breadboard">
                    <geometry x="50" y="50" z="1.5"/>
                </breadboardView>
                <schematicView layer="schematic">
                    <geometry x="300" y="100" z="1.5"/>
                </schematicView>
            </views>
        </instance>

        <!-- Phototransistor -->
        <instance moduleIdRef="PhototransistorModuleID" modelIndex="1002" path="">
            <title>Q1</title>
            <property name="part" value="Phototransistor (TEPT5600)"/>
            <views>
                <breadboardView layer="breadboard">
                    <geometry x="250" y="100" z="2.0"/>
                </breadboardView>
                <schematicView layer="schematic">
                    <geometry x="150" y="80" z="2.0"/>
                </schematicView>
            </views>
        </instance>

        <!-- Load Resistor 1k -->
        <instance moduleIdRef="ResistorModuleID" modelIndex="1003" path="">
            <title>R1</title>
            <property name="resistance" value="1000"/>
            <views>
                <breadboardView layer="breadboard">
                    <geometry x="250" y="180" z="2.0"/>
                </breadboardView>
                <schematicView layer="schematic">
                    <geometry x="150" y="180" z="2.0"/>
                </schematicView>
            </views>
        </instance>

        <!-- Wire 1: 3.3V (Pico Pin 36) -> Phototransistor Collector -->
        <instance moduleIdRef="WireModuleID" modelIndex="2001" path="">
            <title>Wire_3V3</title>
            <views>
                <breadboardView layer="breadboardWire">
                    <wireExtras color="#e53935"/>
                    <connectors>
                        <connector connectorId="connector0">
                            <connects>
                                <connect modelIndex="1001" connectorId="pin36"/>
                                <connect modelIndex="1002" connectorId="collector"/>
                            </connects>
                        </connector>
                    </connectors>
                </breadboardView>
            </views>
        </instance>

        <!-- Wire 2: Phototransistor Emitter -> Resistor Pin 1 -> ADC0 (Pico Pin 31) -->
        <instance moduleIdRef="WireModuleID" modelIndex="2002" path="">
            <title>Wire_Signal</title>
            <views>
                <breadboardView layer="breadboardWire">
                    <wireExtras color="#fdd835"/>
                    <connectors>
                        <connector connectorId="connector0">
                            <connects>
                                <connect modelIndex="1002" connectorId="emitter"/>
                                <connect modelIndex="1003" connectorId="pin1"/>
                                <connect modelIndex="1001" connectorId="pin31"/>
                            </connects>
                        </connector>
                    </connectors>
                </breadboardView>
            </views>
        </instance>

        <!-- Wire 3: Resistor Pin 2 -> GND (Pico Pin 38) -->
        <instance moduleIdRef="WireModuleID" modelIndex="2003" path="">
            <title>Wire_GND</title>
            <views>
                <breadboardView layer="breadboardWire">
                    <wireExtras color="#212121"/>
                    <connectors>
                        <connector connectorId="connector0">
                            <connects>
                                <connect modelIndex="1003" connectorId="pin2"/>
                                <connect modelIndex="1001" connectorId="pin38"/>
                            </connects>
                        </connector>
                    </connectors>
                </breadboardView>
            </views>
        </instance>
    </instances>
</module>
"""

def generate_fritzing_photodiode_tia():
    return """<?xml version="1.0" encoding="UTF-8"?>
<module fritzingVersion="0.9.10" icon="photoquick_tia.png">
    <title>Photoquick - Photodiode TIA Circuit</title>
    <label>PQ-TIA</label>
    <date>2026-10-25</date>
    <author>ritmps / photoquick</author>
    <description>Circuit 2: RP2040 Pico + Photodiode + Rail-to-Rail OpAmp TIA</description>
    <views>
        <view name="breadboardView" zoom="1.0" x="0" y="0"/>
        <view name="schematicView" zoom="1.0" x="0" y="0"/>
        <view name="pcbView" zoom="1.0" x="0" y="0"/>
    </views>
    <instances>
        <!-- Raspberry Pi Pico -->
        <instance moduleIdRef="Raspberry-Pi-Pico_breadboard" modelIndex="1001" path="">
            <title>Pico1</title>
            <views>
                <breadboardView layer="breadboard"><geometry x="50" y="50" z="1.5"/></breadboardView>
            </views>
        </instance>

        <!-- Op-Amp MCP6001 (DIP-8 / SOT-23 Breakout) -->
        <instance moduleIdRef="DIP8_OpAmp_ModuleID" modelIndex="1002" path="">
            <title>U2 (MCP6001)</title>
            <property name="part" value="Microchip MCP6001 Rail-to-Rail OpAmp"/>
            <views>
                <breadboardView layer="breadboard"><geometry x="300" y="120" z="2.0"/></breadboardView>
            </views>
        </instance>

        <!-- Photodiode (BPW34) -->
        <instance moduleIdRef="PhotodiodeModuleID" modelIndex="1003" path="">
            <title>D1</title>
            <property name="part" value="Silicon PIN Photodiode BPW34"/>
            <views>
                <breadboardView layer="breadboard"><geometry x="230" y="100" z="2.0"/></breadboardView>
            </views>
        </instance>

        <!-- Feedback Resistor Rf (100k) -->
        <instance moduleIdRef="ResistorModuleID" modelIndex="1004" path="">
            <title>Rf</title>
            <property name="resistance" value="100000"/>
            <views>
                <breadboardView layer="breadboard"><geometry x="300" y="60" z="2.0"/></breadboardView>
            </views>
        </instance>

        <!-- Feedback Capacitor Cf (2.2pF) -->
        <instance moduleIdRef="CapacitorModuleID" modelIndex="1005" path="">
            <title>Cf</title>
            <property name="capacitance" value="2.2pF"/>
            <views>
                <breadboardView layer="breadboard"><geometry x="300" y="40" z="2.0"/></breadboardView>
            </views>
        </instance>

        <!-- Wires -->
        <instance moduleIdRef="WireModuleID" modelIndex="2001" path="">
            <title>Wire_VDD</title>
            <views>
                <breadboardView layer="breadboardWire">
                    <wireExtras color="#e53935"/>
                    <connectors>
                        <connector connectorId="connector0">
                            <connects>
                                <connect modelIndex="1001" connectorId="pin36"/>
                                <connect modelIndex="1002" connectorId="pin5_VDD"/>
                            </connects>
                        </connector>
                    </connectors>
                </breadboardView>
            </views>
        </instance>

        <instance moduleIdRef="WireModuleID" modelIndex="2002" path="">
            <title>Wire_GND</title>
            <views>
                <breadboardView layer="breadboardWire">
                    <wireExtras color="#212121"/>
                    <connectors>
                        <connector connectorId="connector0">
                            <connects>
                                <connect modelIndex="1001" connectorId="pin38"/>
                                <connect modelIndex="1002" connectorId="pin2_VSS"/>
                                <connect modelIndex="1002" connectorId="pin3_IN_PLUS"/>
                                <connect modelIndex="1003" connectorId="anode"/>
                            </connects>
                        </connector>
                    </connectors>
                </breadboardView>
            </views>
        </instance>

        <instance moduleIdRef="WireModuleID" modelIndex="2003" path="">
            <title>Wire_Output</title>
            <views>
                <breadboardView layer="breadboardWire">
                    <wireExtras color="#1e88e5"/>
                    <connectors>
                        <connector connectorId="connector0">
                            <connects>
                                <connect modelIndex="1002" connectorId="pin1_OUT"/>
                                <connect modelIndex="1004" connectorId="pin2"/>
                                <connect modelIndex="1005" connectorId="pin2"/>
                                <connect modelIndex="1001" connectorId="pin31"/>
                            </connects>
                        </connector>
                    </connectors>
                </breadboardView>
            </views>
        </instance>
    </instances>
</module>
"""

# ---------------------------------------------------------------------------
# 3. High-Quality Standalone SVGs for Immediate Visual Comparison in VSCode
# ---------------------------------------------------------------------------

def generate_svg_kicad_phototransistor():
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 550" width="100%" height="100%">
  <defs>
    <style>
      .bg { fill: #fcfbfa; }
      .border { stroke: #8b0000; stroke-width: 2; fill: none; }
      .grid { stroke: #f0ede8; stroke-width: 0.5; }
      .wire { stroke: #008000; stroke-width: 2.2; fill: none; stroke-linecap: round; }
      .comp { stroke: #8b0000; stroke-width: 2.2; fill: none; stroke-linecap: round; }
      .text-ref { font-family: monospace; font-size: 14px; font-weight: bold; fill: #008080; }
      .text-val { font-family: monospace; font-size: 13px; fill: #0000aa; }
      .text-pin { font-family: monospace; font-size: 11px; fill: #888888; }
      .text-title { font-family: sans-serif; font-size: 16px; font-weight: bold; fill: #333333; }
      .text-meta { font-family: sans-serif; font-size: 12px; fill: #666666; }
      .junction { fill: #008000; }
      .pico-body { fill: #eef7ee; stroke: #006600; stroke-width: 2; }
      .arrow { fill: #8b0000; }
    </style>
  </defs>

  <!-- Sheet Background -->
  <rect width="900" height="550" class="bg"/>
  <rect x="20" y="20" width="860" height="510" class="border"/>

  <!-- Title Block (KiCad Style) -->
  <rect x="520" y="450" width="360" height="80" class="border" stroke-width="1.5"/>
  <line x1="520" y1="480" x2="880" y2="480" stroke="#8b0000" stroke-width="1"/>
  <line x1="520" y1="505" x2="880" y2="505" stroke="#8b0000" stroke-width="1"/>
  <line x1="720" y1="480" x2="720" y2="530" stroke="#8b0000" stroke-width="1"/>
  <text x="530" y="472" class="text-title">Photoquick: Phototransistor (Phase 1)</text>
  <text x="530" y="497" class="text-meta">File: phototransistor.kicad_sch</text>
  <text x="730" y="497" class="text-meta">Rev: 1.0 (KiCad 8.0)</text>
  <text x="530" y="522" class="text-meta">Company: ritmps / photoquick</text>
  <text x="730" y="522" class="text-meta">Date: 2026-10-25</text>

  <!-- Raspberry Pi Pico Symbol Block -->
  <g transform="translate(560, 80)">
    <rect x="0" y="0" width="220" height="300" rx="4" class="pico-body"/>
    <text x="110" y="30" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="bold" fill="#006600">Raspberry Pi Pico</text>
    <text x="110" y="48" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#448844">RP2040 Microcontroller</text>

    <!-- Pin 36: 3V3_OUT -->
    <line x1="-30" y1="80" x2="0" y2="80" class="wire"/>
    <text x="-35" y="75" text-anchor="end" class="text-ref">3V3_OUT</text>
    <text x="8" y="84" class="text-pin">Pin 36</text>

    <!-- Pin 31: ADC0 / GP26 -->
    <line x1="-30" y1="170" x2="0" y2="170" class="wire"/>
    <text x="-35" y="165" text-anchor="end" class="text-ref">GPIO26_ADC0</text>
    <text x="8" y="174" class="text-pin">Pin 31</text>

    <!-- Pin 38: GND -->
    <line x1="-30" y1="250" x2="0" y2="250" class="wire"/>
    <text x="-35" y="245" text-anchor="end" class="text-ref">GND</text>
    <text x="8" y="254" class="text-pin">Pin 38</text>
  </g>

  <!-- Phototransistor Q1 -->
  <g transform="translate(260, 160)">
    <circle cx="0" cy="0" r="32" class="comp"/>
    <line x1="-12" y1="-18" x2="-12" y2="18" stroke="#8b0000" stroke-width="3"/>
    
    <!-- Collector Lead -->
    <line x1="-12" y1="-10" x2="16" y2="-24" class="comp"/>
    <line x1="16" y1="-24" x2="16" y2="-50" class="comp"/>
    
    <!-- Emitter Lead + Arrow -->
    <line x1="-12" y1="10" x2="16" y2="24" class="comp"/>
    <polygon points="16,24 8,16 14,14" class="arrow"/>
    <line x1="16" y1="24" x2="16" y2="50" class="comp"/>

    <!-- Light arrows -->
    <g transform="translate(-40, -35)">
      <line x1="0" y1="0" x2="20" y2="20" class="comp" stroke-width="1.8"/>
      <polygon points="20,20 12,18 18,12" class="arrow"/>
      <line x1="-10" y1="10" x2="10" y2="30" class="comp" stroke-width="1.8"/>
      <polygon points="10,30 2,28 8,22" class="arrow"/>
    </g>

    <text x="35" y="-15" class="text-ref">Q1</text>
    <text x="35" y="5" class="text-val">TEPT5600</text>
    <text x="35" y="22" font-family="sans-serif" font-size="11" fill="#666666">(NPN Phototransistor)</text>
  </g>

  <!-- Load Resistor R1 -->
  <g transform="translate(260, 310)">
    <line x1="16" y1="-30" x2="16" y2="-18" class="comp"/>
    <!-- Resistor Body (ZigZag) -->
    <path d="M 16 -18 L 6 -12 L 26 -6 L 6 0 L 26 6 L 6 12 L 26 18 L 16 24" class="comp"/>
    <line x1="16" y1="24" x2="16" y2="40" class="comp"/>

    <text x="40" y="-5" class="text-ref">R_L (R1)</text>
    <text x="40" y="15" class="text-val">1 kΩ</text>
    <text x="40" y="32" font-family="sans-serif" font-size="11" fill="#666666">(500Ω - 2kΩ)</text>
  </g>

  <!-- Wires & Connections -->
  <!-- 3.3V Line from Pico Pin 36 to Collector -->
  <path d="M 530 160 L 276 160 L 276 110" class="wire"/>
  
  <!-- Output Node from Emitter to Pico Pin 31 -->
  <path d="M 276 210 L 276 280" class="wire"/>
  <path d="M 276 250 L 530 250" class="wire"/>
  <circle cx="276" cy="250" r="4.5" class="junction"/>

  <!-- GND Line from R1 to Pico Pin 38 -->
  <path d="M 276 350 L 276 380 L 530 380 L 530 330" class="wire"/>

  <!-- Explanatory Annotation -->
  <rect x="50" y="420" width="380" height="90" rx="5" fill="#f4f9f4" stroke="#88b088" stroke-width="1"/>
  <text x="65" y="445" font-family="sans-serif" font-size="13" font-weight="bold" fill="#005500">Physical Operating Characteristics:</text>
  <text x="65" y="468" font-family="sans-serif" font-size="12" fill="#333333">• Bandwidth limited to ~50–100 kHz by base charge storage.</text>
  <text x="65" y="488" font-family="sans-serif" font-size="12" fill="#333333">• Fall time: 5–20 µs (recombination decay).</text>
  <text x="65" y="504" font-family="sans-serif" font-size="12" fill="#333333">• Sized for 60/120/240 Hz refresh &amp; LCD G-to-G response.</text>
</svg>
"""

def generate_svg_kicad_photodiode_tia():
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 580" width="100%" height="100%">
  <defs>
    <style>
      .bg { fill: #fcfbfa; }
      .border { stroke: #8b0000; stroke-width: 2; fill: none; }
      .wire { stroke: #008000; stroke-width: 2.2; fill: none; stroke-linecap: round; }
      .comp { stroke: #8b0000; stroke-width: 2.2; fill: none; stroke-linecap: round; }
      .text-ref { font-family: monospace; font-size: 14px; font-weight: bold; fill: #008080; }
      .text-val { font-family: monospace; font-size: 13px; fill: #0000aa; }
      .text-pin { font-family: monospace; font-size: 11px; fill: #888888; }
      .text-title { font-family: sans-serif; font-size: 16px; font-weight: bold; fill: #333333; }
      .text-meta { font-family: sans-serif; font-size: 12px; fill: #666666; }
      .junction { fill: #008000; }
      .pico-body { fill: #eef7ee; stroke: #006600; stroke-width: 2; }
      .opamp-body { fill: #fff5ee; stroke: #8b0000; stroke-width: 2; }
      .arrow { fill: #8b0000; }
    </style>
  </defs>

  <!-- Sheet Background -->
  <rect width="960" height="580" class="bg"/>
  <rect x="20" y="20" width="920" height="540" class="border"/>

  <!-- Title Block (KiCad Style) -->
  <rect x="580" y="470" width="360" height="90" class="border" stroke-width="1.5"/>
  <line x1="580" y1="505" x2="940" y2="505" stroke="#8b0000" stroke-width="1"/>
  <line x1="580" y1="535" x2="940" y2="535" stroke="#8b0000" stroke-width="1"/>
  <line x1="770" y1="505" x2="770" y2="560" stroke="#8b0000" stroke-width="1"/>
  <text x="590" y="495" class="text-title">Photoquick: Photodiode TIA (Phase 2)</text>
  <text x="590" y="525" class="text-meta">File: photodiode_tia.kicad_sch</text>
  <text x="780" y="525" class="text-meta">Rev: 1.0 (KiCad 8.0)</text>
  <text x="590" y="552" class="text-meta">Company: ritmps / photoquick</text>
  <text x="780" y="552" class="text-meta">Date: 2026-10-25</text>

  <!-- Raspberry Pi Pico Symbol Block -->
  <g transform="translate(680, 80)">
    <rect x="0" y="0" width="220" height="340" rx="4" class="pico-body"/>
    <text x="110" y="32" text-anchor="middle" font-family="sans-serif" font-size="15" font-weight="bold" fill="#006600">Raspberry Pi Pico</text>
    <text x="110" y="50" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#448844">RP2040 Microcontroller</text>

    <!-- Pin 36: 3V3_OUT -->
    <line x1="-30" y1="90" x2="0" y2="90" class="wire"/>
    <text x="-35" y="85" text-anchor="end" class="text-ref">3V3_OUT</text>
    <text x="8" y="94" class="text-pin">Pin 36</text>

    <!-- Pin 31: ADC0 / GP26 -->
    <line x1="-30" y1="200" x2="0" y2="200" class="wire"/>
    <text x="-35" y="195" text-anchor="end" class="text-ref">GPIO26_ADC0</text>
    <text x="8" y="204" class="text-pin">Pin 31</text>

    <!-- Pin 38: GND -->
    <line x1="-30" y1="290" x2="0" y2="290" class="wire"/>
    <text x="-35" y="285" text-anchor="end" class="text-ref">GND</text>
    <text x="8" y="294" class="text-pin">Pin 38</text>
  </g>

  <!-- Photodiode D1 (Photovoltaic connection) -->
  <g transform="translate(130, 260)">
    <!-- Photodiode Symbol -->
    <line x1="0" y1="-30" x2="0" y2="-12" class="comp"/>
    <polygon points="-16,-12 16,-12 0,12" class="comp"/>
    <line x1="-16" y1="12" x2="16" y2="12" stroke="#8b0000" stroke-width="2.5"/>
    <line x1="0" y1="12" x2="0" y2="40" class="comp"/>

    <!-- Optical arrows -->
    <g transform="translate(-35, -20)">
      <line x1="0" y1="0" x2="16" y2="16" class="comp" stroke-width="1.6"/>
      <polygon points="16,16 9,14 14,9" class="arrow"/>
      <line x1="-8" y1="8" x2="8" y2="24" class="comp" stroke-width="1.6"/>
      <polygon points="8,24 1,22 6,17" class="arrow"/>
    </g>

    <text x="25" y="-10" class="text-ref">D1</text>
    <text x="25" y="10" class="text-val">BPW34 / TEMD5010</text>
    <text x="25" y="27" font-family="sans-serif" font-size="11" fill="#666666">Anode (top), Cathode (bot)</text>
  </g>

  <!-- Op-Amp Triangle (TIA) -->
  <g transform="translate(350, 270)">
    <polygon points="-40,-60 -40,60 60,0" class="opamp-body"/>
    
    <!-- Inverting Input (-) -->
    <line x1="-70" y1="-30" x2="-40" y2="-30" class="comp"/>
    <text x="-32" y="-24" font-family="monospace" font-size="20" font-weight="bold" fill="#8b0000">-</text>
    <text x="-65" y="-40" class="text-pin">Pin 4</text>

    <!-- Non-Inverting Input (+) -->
    <line x1="-70" y1="30" x2="-40" y2="30" class="comp"/>
    <text x="-32" y="37" font-family="monospace" font-size="20" font-weight="bold" fill="#8b0000">+</text>
    <text x="-65" y="45" class="text-pin">Pin 3</text>

    <!-- Output -->
    <line x1="60" y1="0" x2="90" y2="0" class="comp"/>
    <text x="65" y="-10" class="text-pin">Pin 1</text>

    <!-- Power Pins -->
    <line x1="10" y1="-36" x2="10" y2="-65" class="comp"/>
    <text x="15" y="-55" class="text-pin">V+ (Pin 5)</text>
    <line x1="10" y1="36" x2="10" y2="65" class="comp"/>
    <text x="15" y="60" class="text-pin">V- (Pin 2)</text>

    <text x="10" y="-10" class="text-ref">U2</text>
    <text x="5" y="10" class="text-val">MCP6001</text>
    <text x="5" y="24" font-family="sans-serif" font-size="10" fill="#666666">(RRIO, 5MHz)</text>
  </g>

  <!-- Feedback Resistor Rf -->
  <g transform="translate(360, 160)">
    <line x1="-60" y1="0" x2="-35" y2="0" class="comp"/>
    <!-- Resistor box -->
    <rect x="-35" y="-10" width="70" height="20" class="comp" fill="#ffffff"/>
    <line x1="35" y1="0" x2="60" y2="0" class="comp"/>
    <text x="0" y="-15" text-anchor="middle" class="text-ref">R_f</text>
    <text x="0" y="5" text-anchor="middle" class="text-val">100 kΩ – 470 kΩ</text>
  </g>

  <!-- Feedback Capacitor Cf -->
  <g transform="translate(360, 100)">
    <line x1="-60" y1="0" x2="-10" y2="0" class="comp"/>
    <!-- Capacitor plates -->
    <line x1="-10" y1="-15" x2="-10" y2="15" stroke="#8b0000" stroke-width="2.5"/>
    <line x1="10" y1="-15" x2="10" y2="15" stroke="#8b0000" stroke-width="2.5"/>
    <line x1="10" y1="0" x2="60" y2="0" class="comp"/>
    <text x="0" y="-20" text-anchor="middle" class="text-ref">C_f</text>
    <text x="0" y="30" text-anchor="middle" class="text-val">2.2 pF (Phase Margin)</text>
  </g>

  <!-- Bypass Capacitor C_dec -->
  <g transform="translate(480, 140)">
    <line x1="0" y1="-15" x2="0" y2="-6" class="comp"/>
    <line x1="-12" y1="-6" x2="12" y2="-6" stroke="#8b0000" stroke-width="2.2"/>
    <line x1="-12" y1="6" x2="12" y2="6" stroke="#8b0000" stroke-width="2.2"/>
    <line x1="0" y1="6" x2="0" y2="15" class="comp"/>
    <text x="18" y="4" class="text-val">0.1 µF</text>
    <text x="18" y="-10" class="text-ref">C_bypass</text>
  </g>

  <!-- WIRING -->
  <!-- Cathode to Inverting Input (-) via Virtual Ground -->
  <path d="M 130 300 L 190 300 L 190 240 L 280 240" class="wire"/>
  
  <!-- Inverting Input up to Feedback network -->
  <path d="M 230 240 L 230 160 L 300 160" class="wire"/>
  <path d="M 230 160 L 230 100 L 300 100" class="wire"/>
  <circle cx="230" cy="240" r="4" class="junction"/>
  <circle cx="230" cy="160" r="4" class="junction"/>

  <!-- Feedback Output junction -->
  <path d="M 420 100 L 490 100 L 490 160" class="wire"/>
  <path d="M 420 160 L 490 160" class="wire"/>
  <path d="M 490 160 L 490 270" class="wire"/>
  <path d="M 440 270 L 650 270" class="wire"/>
  <circle cx="490" cy="160" r="4" class="junction"/>
  <circle cx="490" cy="270" r="4" class="junction"/>

  <!-- V+ (Pin 5) to 3.3V Line -->
  <path d="M 360 205 L 360 170 L 650 170" class="wire"/>
  <path d="M 480 125 L 480 170" class="wire"/>
  <circle cx="480" cy="170" r="4" class="junction"/>

  <!-- GND BUS: D1 Anode, OpAmp (+), OpAmp V-, Bypass, Pico Pin 38 -->
  <path d="M 130 230 L 130 200 L 80 200 L 80 370 L 650 370" class="wire"/>
  <path d="M 280 300 L 250 300 L 250 370" class="wire"/>
  <path d="M 360 335 L 360 370" class="wire"/>
  <path d="M 480 155 L 480 370" class="wire"/>
  <circle cx="250" cy="370" r="4" class="junction"/>
  <circle cx="360" cy="370" r="4" class="junction"/>
  <circle cx="480" cy="370" r="4" class="junction"/>

  <!-- Annotations -->
  <rect x="50" y="440" width="460" height="95" rx="5" fill="#f4f9f4" stroke="#88b088" stroke-width="1"/>
  <text x="65" y="465" font-family="sans-serif" font-size="13" font-weight="bold" fill="#005500">TIA High-Speed Theory of Operation:</text>
  <text x="65" y="488" font-family="sans-serif" font-size="12" fill="#333333">• Virtual Ground held at 0V keeps diode junction voltage at 0V.</text>
  <text x="65" y="506" font-family="sans-serif" font-size="12" fill="#333333">• Zero-swing eliminates junction capacitor charging lag (MHz response).</text>
  <text x="65" y="524" font-family="sans-serif" font-size="12" fill="#333333">• V_out = I_photo * R_f (Active High 0 to 3.3V directly into ADC0).</text>
</svg>
"""

def generate_svg_fritzing_phototransistor():
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 560" width="100%" height="100%">
  <defs>
    <style>
      .bb-bg { fill: #f5f3e9; stroke: #c8c2b0; stroke-width: 2; }
      .bb-rail-red { stroke: #d32f2f; stroke-width: 2.5; }
      .bb-rail-blue { stroke: #1976d2; stroke-width: 2.5; }
      .bb-hole { fill: #2b2b2b; stroke: #8c857b; stroke-width: 0.8; }
      .pico-pcb { fill: #00753a; stroke: #004d26; stroke-width: 2; }
      .pico-chip { fill: #1a1a1a; stroke: #333333; stroke-width: 1; }
      .pico-usb { fill: #b0bec5; stroke: #78909c; stroke-width: 1.5; }
      .pico-pad { fill: #ffd54f; stroke: #c6a700; stroke-width: 1; }
      .wire-red { stroke: #e53935; stroke-width: 4.5; fill: none; stroke-linecap: round; filter: drop-shadow(1px 2px 2px rgba(0,0,0,0.3)); }
      .wire-blk { stroke: #212121; stroke-width: 4.5; fill: none; stroke-linecap: round; filter: drop-shadow(1px 2px 2px rgba(0,0,0,0.3)); }
      .wire-yel { stroke: #fbc02d; stroke-width: 4.5; fill: none; stroke-linecap: round; filter: drop-shadow(1px 2px 2px rgba(0,0,0,0.3)); }
      .label { font-family: sans-serif; font-size: 13px; font-weight: bold; }
    </style>
  </defs>

  <rect width="950" height="560" fill="#e8eaed"/>
  
  <!-- Breadboard Base -->
  <rect x="40" y="40" width="870" height="480" rx="10" class="bb-bg"/>

  <!-- Power Rails (Top & Bottom) -->
  <line x1="70" y1="65" x2="880" y2="65" class="bb-rail-red"/>
  <line x1="70" y1="85" x2="880" y2="85" class="bb-rail-blue"/>
  <line x1="70" y1="475" x2="880" y2="475" class="bb-rail-red"/>
  <line x1="70" y1="495" x2="880" y2="495" class="bb-rail-blue"/>

  <!-- Breadboard Center Divider Groove -->
  <rect x="60" y="270" width="830" height="18" fill="#dfdac8"/>

  <!-- Breadboard Pin Holes (Simplified visual array) -->
  <g opacity="0.6">
    <!-- Top section holes -->
    <circle cx="100" cy="115" r="3.5" class="bb-hole"/><circle cx="100" cy="140" r="3.5" class="bb-hole"/>
    <circle cx="100" cy="165" r="3.5" class="bb-hole"/><circle cx="100" cy="190" r="3.5" class="bb-hole"/>
    <circle cx="100" cy="215" r="3.5" class="bb-hole"/><circle cx="100" cy="240" r="3.5" class="bb-hole"/>
    <!-- Bottom section holes -->
    <circle cx="100" cy="305" r="3.5" class="bb-hole"/><circle cx="100" cy="330" r="3.5" class="bb-hole"/>
    <circle cx="100" cy="355" r="3.5" class="bb-hole"/><circle cx="100" cy="380" r="3.5" class="bb-hole"/>
    <circle cx="100" cy="405" r="3.5" class="bb-hole"/><circle cx="100" cy="430" r="3.5" class="bb-hole"/>
  </g>

  <!-- Raspberry Pi Pico Board Representation -->
  <g transform="translate(140, 110)">
    <rect x="0" y="0" width="160" height="340" rx="6" class="pico-pcb"/>
    <rect x="45" y="-12" width="70" height="40" rx="3" class="pico-usb"/>
    <rect x="45" y="100" width="70" height="70" rx="2" class="pico-chip"/>
    <text x="80" y="140" text-anchor="middle" fill="#888888" font-family="monospace" font-size="11">RP2040</text>
    <text x="80" y="240" text-anchor="middle" fill="#ffffff" font-family="sans-serif" font-size="14" font-weight="bold">Raspberry Pi</text>
    <text x="80" y="260" text-anchor="middle" fill="#ffffff" font-family="sans-serif" font-size="13">Pico</text>

    <!-- Pins on Right Edge -->
    <!-- Pin 36 (3V3 Out) -->
    <rect x="145" y="120" width="15" height="10" class="pico-pad"/>
    <text x="135" y="130" text-anchor="end" fill="#ffffff" font-family="monospace" font-size="11">36 (3V3)</text>

    <!-- Pin 31 (GPIO26 / ADC0) -->
    <rect x="145" y="210" width="15" height="10" class="pico-pad"/>
    <text x="135" y="220" text-anchor="end" fill="#ffffff" font-family="monospace" font-size="11">31 (ADC0)</text>

    <!-- Pin 38 (GND) -->
    <rect x="145" y="280" width="15" height="10" class="pico-pad"/>
    <text x="135" y="290" text-anchor="end" fill="#ffffff" font-family="monospace" font-size="11">38 (GND)</text>
  </g>

  <!-- Physical Phototransistor (5mm clear epoxy package) -->
  <g transform="translate(520, 180)">
    <circle cx="0" cy="0" r="22" fill="#cce5ff" stroke="#3399ff" stroke-width="2.5" opacity="0.85"/>
    <circle cx="0" cy="0" r="16" fill="#b3d9ff" stroke="#3399ff" stroke-width="1.5"/>
    <rect x="-6" y="-6" width="12" height="12" fill="#1a1a1a"/>
    <text x="35" y="-5" class="label" fill="#003366">Phototransistor (Q1)</text>
    <text x="35" y="15" font-family="sans-serif" font-size="12" fill="#555555">Long lead = Collector</text>
    <text x="35" y="30" font-family="sans-serif" font-size="12" fill="#555555">Short lead (flat) = Emitter</text>
  </g>

  <!-- Physical 1k Resistor (Thru-hole 1/4W: Brown, Black, Red, Gold) -->
  <g transform="translate(520, 320)">
    <!-- Leads -->
    <line x1="-40" y1="0" x2="40" y2="0" stroke="#b0bec5" stroke-width="3"/>
    <!-- Body -->
    <rect x="-24" y="-8" width="48" height="16" rx="4" fill="#d7ccc8" stroke="#8d6e63" stroke-width="1.5"/>
    <!-- Color Bands: Brown (1), Black (0), Red (x100), Gold (5%) -->
    <rect x="-16" y="-8" width="5" height="16" fill="#5d4037"/>
    <rect x="-6" y="-8" width="5" height="16" fill="#212121"/>
    <rect x="4" y="-8" width="5" height="16" fill="#d32f2f"/>
    <rect x="15" y="-8" width="4" height="16" fill="#ffd700"/>

    <text x="50" y="5" class="label" fill="#4e342e">R1: 1 kΩ (Load)</text>
  </g>

  <!-- Fritzing-Style Flexible Jumper Wires -->
  <!-- Red Wire: Pico Pin 36 -> Phototransistor Collector -->
  <path d="M 300 235 C 380 235, 430 170, 505 170" class="wire-red"/>

  <!-- Yellow Wire: Phototransistor Emitter -> Resistor Lead 1 & Pico Pin 31 (ADC0) -->
  <path d="M 505 195 C 470 240, 480 320, 480 320" class="wire-yel"/>
  <path d="M 480 320 C 440 320, 370 325, 300 325" class="wire-yel"/>

  <!-- Black Wire: Resistor Lead 2 -> Pico Pin 38 (GND) -->
  <path d="M 560 320 C 620 320, 620 420, 460 420 C 370 420, 350 395, 300 395" class="wire-blk"/>

  <!-- Banner / Header -->
  <text x="60" y="35" font-family="sans-serif" font-size="18" font-weight="bold" fill="#333333">Fritzing Breadboard View: Phototransistor (Circuit 1)</text>
</svg>
"""

def generate_svg_fritzing_photodiode_tia():
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 580" width="100%" height="100%">
  <defs>
    <style>
      .bb-bg { fill: #f5f3e9; stroke: #c8c2b0; stroke-width: 2; }
      .bb-rail-red { stroke: #d32f2f; stroke-width: 2.5; }
      .bb-rail-blue { stroke: #1976d2; stroke-width: 2.5; }
      .pico-pcb { fill: #00753a; stroke: #004d26; stroke-width: 2; }
      .pico-chip { fill: #1a1a1a; stroke: #333333; stroke-width: 1; }
      .pico-usb { fill: #b0bec5; stroke: #78909c; stroke-width: 1.5; }
      .pico-pad { fill: #ffd54f; stroke: #c6a700; stroke-width: 1; }
      .ic-body { fill: #212121; stroke: #424242; stroke-width: 1.5; }
      .ic-pin { fill: #cfd8dc; stroke: #78909c; stroke-width: 1; }
      .wire-red { stroke: #e53935; stroke-width: 4.5; fill: none; stroke-linecap: round; filter: drop-shadow(1px 2px 2px rgba(0,0,0,0.3)); }
      .wire-blk { stroke: #212121; stroke-width: 4.5; fill: none; stroke-linecap: round; filter: drop-shadow(1px 2px 2px rgba(0,0,0,0.3)); }
      .wire-blu { stroke: #1976d2; stroke-width: 4.5; fill: none; stroke-linecap: round; filter: drop-shadow(1px 2px 2px rgba(0,0,0,0.3)); }
      .wire-grn { stroke: #43a047; stroke-width: 4.5; fill: none; stroke-linecap: round; filter: drop-shadow(1px 2px 2px rgba(0,0,0,0.3)); }
      .label { font-family: sans-serif; font-size: 13px; font-weight: bold; }
    </style>
  </defs>

  <rect width="980" height="580" fill="#e8eaed"/>
  
  <!-- Breadboard Base -->
  <rect x="30" y="40" width="920" height="500" rx="10" class="bb-bg"/>

  <!-- Power Rails -->
  <line x1="60" y1="65" x2="920" y2="65" class="bb-rail-red"/>
  <line x1="60" y1="85" x2="920" y2="85" class="bb-rail-blue"/>
  <line x1="60" y1="495" x2="920" y2="495" class="bb-rail-red"/>
  <line x1="60" y1="515" x2="920" y2="515" class="bb-rail-blue"/>

  <!-- Center Divider -->
  <rect x="50" y="285" width="880" height="18" fill="#dfdac8"/>

  <!-- Raspberry Pi Pico -->
  <g transform="translate(100, 120)">
    <rect x="0" y="0" width="150" height="340" rx="6" class="pico-pcb"/>
    <rect x="40" y="-12" width="70" height="40" rx="3" class="pico-usb"/>
    <rect x="40" y="100" width="70" height="70" rx="2" class="pico-chip"/>
    <text x="75" y="140" text-anchor="middle" fill="#888888" font-family="monospace" font-size="11">RP2040</text>
    <text x="75" y="240" text-anchor="middle" fill="#ffffff" font-family="sans-serif" font-size="14" font-weight="bold">Raspberry Pi</text>
    <text x="75" y="260" text-anchor="middle" fill="#ffffff" font-family="sans-serif" font-size="13">Pico</text>

    <!-- Pins -->
    <rect x="135" y="120" width="15" height="10" class="pico-pad"/>
    <text x="125" y="130" text-anchor="end" fill="#ffffff" font-family="monospace" font-size="11">36 (3V3)</text>
    <rect x="135" y="210" width="15" height="10" class="pico-pad"/>
    <text x="125" y="220" text-anchor="end" fill="#ffffff" font-family="monospace" font-size="11">31 (ADC0)</text>
    <rect x="135" y="280" width="15" height="10" class="pico-pad"/>
    <text x="125" y="290" text-anchor="end" fill="#ffffff" font-family="monospace" font-size="11">38 (GND)</text>
  </g>

  <!-- DIP-8 Op-Amp (MCP6001 / OPA350) straddling center divider -->
  <g transform="translate(480, 255)">
    <!-- DIP-8 Body -->
    <rect x="0" y="0" width="90" height="75" rx="3" class="ic-body"/>
    <circle cx="10" cy="37" r="5" fill="#111111"/> <!-- Notch -->
    <!-- Pins Top: 1 (Out), 2 (-In), 3 (+In), 4 (Vss/GND) -->
    <rect x="12" y="-10" width="8" height="12" class="ic-pin"/>
    <rect x="32" y="-10" width="8" height="12" class="ic-pin"/>
    <rect x="52" y="-10" width="8" height="12" class="ic-pin"/>
    <rect x="72" y="-10" width="8" height="12" class="ic-pin"/>
    <!-- Pins Bottom: 8 (NC/Vdd), 7 (NC), 6 (NC), 5 (Vdd) -->
    <rect x="12" y="73" width="8" height="12" class="ic-pin"/>
    <rect x="32" y="73" width="8" height="12" class="ic-pin"/>
    <rect x="52" y="73" width="8" height="12" class="ic-pin"/>
    <rect x="72" y="73" width="8" height="12" class="ic-pin"/>

    <text x="45" y="42" text-anchor="middle" fill="#ffffff" font-family="monospace" font-size="12" font-weight="bold">MCP6001</text>
    <text x="16" y="16" fill="#888888" font-family="monospace" font-size="9">1</text>
    <text x="76" y="16" fill="#888888" font-family="monospace" font-size="9">4</text>
    <text x="16" y="65" fill="#888888" font-family="monospace" font-size="9">5</text>
    <text x="76" y="65" fill="#888888" font-family="monospace" font-size="9">8</text>
  </g>

  <!-- Photodiode BPW34 (Flat square silicon PIN package) -->
  <g transform="translate(350, 180)">
    <rect x="-18" y="-18" width="36" height="36" rx="2" fill="#102040" stroke="#4fc3f7" stroke-width="2"/>
    <circle cx="0" cy="0" r="12" fill="#0d1b2a"/>
    <text x="0" y="32" text-anchor="middle" class="label" fill="#0277bd">BPW34</text>
    <text x="0" y="45" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555555">Photodiode</text>
  </g>

  <!-- Feedback Resistor Rf (100k: Brown, Black, Yellow, Gold) -->
  <g transform="translate(520, 160)">
    <line x1="-30" y1="0" x2="30" y2="0" stroke="#b0bec5" stroke-width="2.5"/>
    <rect x="-18" y="-6" width="36" height="12" rx="3" fill="#d7ccc8" stroke="#8d6e63" stroke-width="1.2"/>
    <rect x="-12" y="-6" width="4" height="12" fill="#5d4037"/>
    <rect x="-4" y="-6" width="4" height="12" fill="#212121"/>
    <rect x="4" y="-6" width="4" height="12" fill="#fbc02d"/>
    <rect x="12" y="-6" width="3" height="12" fill="#ffd700"/>
    <text x="40" y="4" class="label" fill="#5d4037">Rf: 100 kΩ</text>
  </g>

  <!-- Feedback Capacitor Cf (Ceramic Disc 2.2pF) -->
  <g transform="translate(520, 115)">
    <line x1="-25" y1="0" x2="25" y2="0" stroke="#b0bec5" stroke-width="2.5"/>
    <circle cx="0" cy="0" r="10" fill="#ffb74d" stroke="#f57c00" stroke-width="1.5"/>
    <text x="0" y="3" text-anchor="middle" font-family="monospace" font-size="8" font-weight="bold">2p2</text>
    <text x="35" y="4" class="label" fill="#e65100">Cf: 2.2 pF</text>
  </g>

  <!-- JUMPER WIRES -->
  <!-- 3.3V (Red): Pico Pin 36 -> Op-Amp Vdd (Pin 5) -->
  <path d="M 250 240 C 320 240, 420 340, 496 340" class="wire-red"/>

  <!-- Output (Blue): Op-Amp Pin 1 (Out) -> Pico Pin 31 (ADC0) -->
  <path d="M 496 245 C 440 210, 360 330, 250 330" class="wire-blu"/>

  <!-- Feedback loops to Pin 1 and Pin 2 -->
  <path d="M 496 245 L 496 160" class="wire-blu" stroke-width="3"/>
  <path d="M 516 245 C 516 190, 546 160, 546 160" class="wire-grn" stroke-width="3"/>
  <path d="M 496 160 L 496 115" class="wire-blu" stroke-width="2"/>
  <path d="M 546 160 L 546 115" class="wire-grn" stroke-width="2"/>

  <!-- Photodiode Cathode to Op-Amp Pin 2 (-In) -->
  <path d="M 350 195 C 410 210, 450 245, 516 245" class="wire-grn"/>

  <!-- GND (Black): Photodiode Anode, Op-Amp Pin 3 (+In), Pin 4 (Vss) -> Pico Pin 38 -->
  <path d="M 350 165 C 330 140, 310 400, 250 400" class="wire-blk"/>
  <path d="M 536 245 C 536 270, 556 245, 556 245" class="wire-blk" stroke-width="3"/>
  <path d="M 556 245 C 570 300, 500 400, 250 400" class="wire-blk"/>

  <!-- Header -->
  <text x="50" y="35" font-family="sans-serif" font-size="18" font-weight="bold" fill="#333333">Fritzing Breadboard View: Photodiode TIA (Circuit 2)</text>
</svg>
"""

# ---------------------------------------------------------------------------
# Execution: Write files to disk
# ---------------------------------------------------------------------------

def main():
    print("Generating KiCad files...")
    with open(os.path.join(KICAD_DIR, "photoquick.kicad_pro"), "w") as f:
        f.write(KICAD_PRO)
    with open(os.path.join(KICAD_DIR, "phototransistor.kicad_sch"), "w") as f:
        f.write(generate_kicad_phototransistor())
    with open(os.path.join(KICAD_DIR, "photodiode_tia.kicad_sch"), "w") as f:
        f.write(generate_kicad_photodiode_tia())

    print("Generating Fritzing files...")
    pt_fz = generate_fritzing_phototransistor()
    tia_fz = generate_fritzing_photodiode_tia()
    
    pt_fz_path = os.path.join(FRITZING_DIR, "phototransistor.fz")
    tia_fz_path = os.path.join(FRITZING_DIR, "photodiode_tia.fz")
    with open(pt_fz_path, "w") as f:
        f.write(pt_fz)
    with open(tia_fz_path, "w") as f:
        f.write(tia_fz)

    # Package as .fzz (standard Fritzing zip format)
    with zipfile.ZipFile(os.path.join(FRITZING_DIR, "phototransistor.fzz"), "w") as z:
        z.writestr("phototransistor.fz", pt_fz)
    with zipfile.ZipFile(os.path.join(FRITZING_DIR, "photodiode_tia.fzz"), "w") as z:
        z.writestr("photodiode_tia.fz", tia_fz)

    print("Generating Standalone SVG Diagrams for instant preview...")
    with open(os.path.join(DIAGRAMS_DIR, "kicad_phototransistor_schematic.svg"), "w") as f:
        f.write(generate_svg_kicad_phototransistor())
    with open(os.path.join(DIAGRAMS_DIR, "kicad_photodiode_tia_schematic.svg"), "w") as f:
        f.write(generate_svg_kicad_photodiode_tia())
    with open(os.path.join(DIAGRAMS_DIR, "fritzing_phototransistor_breadboard.svg"), "w") as f:
        f.write(generate_svg_fritzing_phototransistor())
    with open(os.path.join(DIAGRAMS_DIR, "fritzing_photodiode_tia_breadboard.svg"), "w") as f:
        f.write(generate_svg_fritzing_photodiode_tia())

    print("All files generated successfully!")

if __name__ == "__main__":
    main()

