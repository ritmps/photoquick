(* ::Package:: *)
(* photoquick.wl - Wolfram Language interface for Pico Light Sensor *)

BeginPackage["Photoquick`"];

FindPicoPort::usage = "FindPicoPort[] attempts to locate the Raspberry Pi Pico /dev/cu.usbmodem* device on macOS.";
PhotoquickCapture::usage = "PhotoquickCapture[port:Automatic, opts] triggers a capture on the Pico and returns an Association with sample data and metadata.";
PhotoquickPlot::usage = "PhotoquickPlot[data] generates a ListLinePlot of voltage versus time for captured photoquick data.";

Begin["`Private`"];

FindPicoPort[] := Module[{ports},
  ports = FileNames["cu.usbmodem*", "/dev"];
  If[Length[ports] == 0,
    None,
    First[ports]
  ]
];

Options[PhotoquickCapture] = {
  "BaudRate" -> 115200,
  "NumSamples" -> 100000,
  "VRef" -> 3.3,
  "ADCMax" -> 4095.0,
  "Timeout" -> 10
};

PhotoquickCapture[portInput_: Automatic, OptionsPattern[]] := Module[
  {port, dev, magic, sampleRate, rawCounts, volts, timeAxis, numSamples},
  
  port = If[portInput === Automatic, FindPicoPort[], portInput];
  If[port === None || !StringQ[port],
    MessageDialog["Photoquick: No Pico USB serial device found in /dev/cu.usbmodem*."];
    Return[$Failed]
  ];

  numSamples = OptionValue["NumSamples"];

  dev = DeviceOpen["Serial", {port, "BaudRate" -> OptionValue["BaudRate"]}];
  If[FailureQ[dev],
    MessageDialog["Photoquick: Failed to open serial port: " <> port];
    Return[$Failed]
  ];

  (* Send 'c' to trigger capture & binary dump *)
  DeviceWrite[dev, "c"];

  (* Read 8-byte header: 4-byte ASCII magic 'PQ01', 4-byte uint32 sample rate *)
  magic = FromCharacterCode[BinaryReadList[dev, "Byte", 4]];
  If[magic =!= "PQ01",
    DeviceClose[dev];
    Print["Photoquick warning: Unexpected header magic: ", InputForm[magic]];
    Return[$Failed]
  ];

  sampleRate = First @ BinaryReadList[dev, "UnsignedInteger32", 1];
  
  (* Read 16-bit ADC samples *)
  rawCounts = BinaryReadList[dev, "UnsignedInteger16", numSamples];
  DeviceClose[dev];

  volts = rawCounts * (OptionValue["VRef"] / OptionValue["ADCMax"]);
  timeAxis = Range[0, Length[volts] - 1] / sampleRate;

  <|
    "Port" -> port,
    "SampleRate" -> sampleRate,
    "NumSamples" -> Length[rawCounts],
    "Duration" -> (Length[rawCounts] / sampleRate),
    "RawCounts" -> rawCounts,
    "Volts" -> volts,
    "Time" -> timeAxis
  |>
];

PhotoquickPlot[data_Association, opts: OptionsPattern[ListLinePlot]] := Module[
  {pts},
  pts = Transpose[{data["Time"], data["Volts"]}];
  ListLinePlot[pts,
    AxesLabel -> {"Time (s)", "Luminance Signal (V)"},
    PlotRange -> All,
    PlotLabel -> StringTemplate["Photoquick: `` samples @ `` Hz (`` s)"][
      data["NumSamples"], data["SampleRate"], NumberForm[data["Duration"], {3, 2}]
    ],
    opts
  ]
];

End[];

EndPackage[];
