(* ::Package:: *)
(* photoquick.wl - Wolfram Language interface & display metrology suite for Pico Light Sensor *)

BeginPackage["Photoquick`"];

FindPicoPort::usage = "FindPicoPort[] attempts to locate the Raspberry Pi Pico /dev/cu.usbmodem* device on macOS.";
PhotoquickSetRate::usage = "PhotoquickSetRate[rateHz, port:Automatic] sets the Pico ADC sample rate (20000, 50000, 100000, or 500000 Hz).";
PhotoquickCapture::usage = "PhotoquickCapture[port:Automatic, opts] triggers a capture on the Pico and returns an Association with sample data and metadata.";
PhotoquickPlot::usage = "PhotoquickPlot[data, opts] generates a ListLinePlot of voltage versus time for captured photoquick data.";
PhotoquickFlickerAnalysis::usage = "PhotoquickFlickerAnalysis[flickerData] or PhotoquickFlickerAnalysis[blackData, whiteData, flickerData] analyzes temporal luminance integration, rise/fall times, and frame-rate aliasing.";
PhotoquickFlickerDashboard::usage = "PhotoquickFlickerDashboard[analysis] renders a multi-panel diagnostic plot of waveform integration, frame hold durations, and rise/fall transitions.";
PhotoquickGenerateStimulus::usage = "PhotoquickGenerateStimulus[file, opts] exports a frame-exact alternating Black/White stimulus video (FullField, Checkerboard, or Stripes) at a specified frame rate.";

Begin["`Private`"];

FindPicoPort[] := Module[{ports},
  ports = FileNames["cu.usbmodem*", "/dev"];
  If[Length[ports] == 0,
    None,
    First[ports]
  ]
];

PhotoquickSetRate[rateHz_Integer, portInput_: Automatic] := Module[
  {port, cmdChar, pyCode, res},
  port = If[portInput === Automatic, FindPicoPort[], portInput];
  If[port === None || !StringQ[port],
    Print["Photoquick: No Pico USB serial device found in /dev/cu.usbmodem*."];
    Return[$Failed]
  ];
  cmdChar = Switch[rateHz,
    20000, "1",
    50000, "2",
    100000, "3",
    500000, "4",
    _,
    Print["Photoquick: Unsupported rate ", rateHz, ". Use 20000, 50000, 100000, or 500000."];
    Return[$Failed]
  ];
  pyCode = StringJoin[
    "import os, sys, tty, termios, fcntl, select, struct, time\n",
    "port, cmd = sys.argv[1], sys.argv[2].encode()\n",
    "fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)\n",
    "tty.setraw(fd)\n",
    "attrs = termios.tcgetattr(fd)\n",
    "attrs[4] = attrs[5] = termios.B115200\n",
    "attrs[2] |= termios.CLOCAL | termios.CREAD\n",
    "termios.tcsetattr(fd, termios.TCSANOW, attrs)\n",
    "status = struct.unpack('I', fcntl.ioctl(fd, termios.TIOCMGET, struct.pack('I', 0)))[0]\n",
    "fcntl.ioctl(fd, termios.TIOCMSET, struct.pack('I', status | termios.TIOCM_DTR | termios.TIOCM_RTS))\n",
    "time.sleep(0.05)\n",
    "termios.tcflush(fd, termios.TCIOFLUSH)\n",
    "os.write(fd, cmd)\n",
    "time.sleep(0.15)\n",
    "r, _, _ = select.select([fd], [], [], 0.5)\n",
    "out = os.read(fd, 4096) if r else b''\n",
    "os.close(fd)\n",
    "sys.stdout.buffer.write(out)\n"
  ];
  res = RunProcess[{"/usr/bin/python3", "-c", pyCode, port, cmdChar}];
  If[FailureQ[res] || res["ExitCode"] =!= 0, Return[$Failed]];
  rateHz
];

Options[PhotoquickCapture] = {
  "BaudRate" -> 115200,
  "NumSamples" -> 100000,
  "SampleRate" -> Automatic,
  "VRef" -> 3.3,
  "ADCMax" -> 4095.0,
  "Timeout" -> 10,
  "WaitForFlicker" -> False,
  "MinSpanVolts" -> 0.25
};

PhotoquickCapture[portInput_: Automatic, OptionsPattern[]] := Module[
  {port, numSamples, timeout, waitFlicker, minSpanV, reqRate, tmpFile, pyCode, res, rawBytes, magic, sampleRate, rawCounts, volts, timeAxis, expectedBytes},
  
  port = If[portInput === Automatic, FindPicoPort[], portInput];
  If[port === None || !StringQ[port],
    Print["Photoquick: No Pico USB serial device found in /dev/cu.usbmodem*."];
    Return[$Failed]
  ];

  reqRate = OptionValue["SampleRate"];
  If[IntegerQ[reqRate],
    PhotoquickSetRate[reqRate, port];
  ];

  numSamples = OptionValue["NumSamples"];
  timeout = OptionValue["Timeout"];
  waitFlicker = TrueQ[OptionValue["WaitForFlicker"]];
  minSpanV = N[OptionValue["MinSpanVolts"]];
  expectedBytes = 8 + numSamples * 2;
  tmpFile = FileNameJoin[{$TemporaryDirectory, "photoquick_capture.bin"}];
  If[FileExistsQ[tmpFile], DeleteFile[tmpFile]];

  (* Use POSIX termios + DTR/RTS assertion so Arduino-Mbed USBCDC streams binary payload to tmpFile *)
  pyCode = StringJoin[
    "import os, sys, tty, termios, fcntl, select, struct, time\n",
    "port, out_path, target, timeout = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])\n",
    "wait_flicker, min_span_v = (sys.argv[5] == '1'), float(sys.argv[6])\n",
    "def grab_once():\n",
    "    fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)\n",
    "    tty.setraw(fd)\n",
    "    attrs = termios.tcgetattr(fd)\n",
    "    attrs[4] = attrs[5] = termios.B115200\n",
    "    attrs[2] |= termios.CLOCAL | termios.CREAD\n",
    "    termios.tcsetattr(fd, termios.TCSANOW, attrs)\n",
    "    status = struct.unpack('I', fcntl.ioctl(fd, termios.TIOCMGET, struct.pack('I', 0)))[0]\n",
    "    fcntl.ioctl(fd, termios.TIOCMSET, struct.pack('I', status | termios.TIOCM_DTR | termios.TIOCM_RTS))\n",
    "    time.sleep(0.04)\n",
    "    termios.tcflush(fd, termios.TCIOFLUSH)\n",
    "    os.write(fd, b'c')\n",
    "    buf = bytearray()\n",
    "    t0 = time.time()\n",
    "    while len(buf) < target and (time.time() - t0) < 2.5:\n",
    "        wait_s = 0.15 if len(buf) >= 8 else 0.5\n",
    "        r, _, _ = select.select([fd], [], [], wait_s)\n",
    "        if r:\n",
    "            chunk = os.read(fd, 65536)\n",
    "            if chunk: buf.extend(chunk)\n",
    "        elif len(buf) >= 8:\n",
    "            break\n",
    "    os.close(fd)\n",
    "    return bytes(buf[:target])\n",
    "def span_volts(b):\n",
    "    if len(b) < 1000 or b[:4] != b'PQ01': return 0.0, 0\n",
    "    n = (len(b) - 8) // 2\n",
    "    c = struct.unpack(f'<{n}H', b[8:8+2*n])\n",
    "    sc = sorted(c)\n",
    "    p05, p95 = sc[int(0.05*n)], sc[int(0.95*n)]\n",
    "    s_all = (p95 - p05) * (3.3 / 4095.0)\n",
    "    if s_all < min_span_v: return s_all, 0\n",
    "    mid = 0.5 * (p05 + p95)\n",
    "    hyst = 0.18 * (p95 - p05)\n",
    "    th_hi, th_lo = mid + hyst, mid - hyst\n",
    "    state = 1 if c[0] >= mid else 0\n",
    "    edges = 0\n",
    "    for x in c[::10]:\n",
    "        if state == 0 and x >= th_hi:\n",
    "            state = 1; edges += 1\n",
    "        elif state == 1 and x <= th_lo:\n",
    "            state = 0; edges += 1\n",
    "    return s_all, edges\n",
    "t_start = time.time()\n",
    "buf = b''\n",
    "while True:\n",
    "    buf = grab_once()\n",
    "    if not wait_flicker: break\n",
    "    s_all, edges = span_volts(buf)\n",
    "    if s_all >= min_span_v and edges >= 8:\n",
    "        buf2 = grab_once()\n",
    "        s2, e2 = span_volts(buf2)\n",
    "        if s2 >= min_span_v and e2 >= 8:\n",
    "            buf = buf2\n",
    "        break\n",
    "    if (time.time() - t_start) >= timeout:\n",
    "        break\n",
    "with open(out_path, 'wb') as f:\n",
    "    f.write(buf)\n"
  ];

  res = RunProcess[{"/usr/bin/python3", "-c", pyCode, port, tmpFile, ToString[expectedBytes], ToString[timeout], If[waitFlicker, "1", "0"], ToString[minSpanV]}];
  If[FailureQ[res] || res["ExitCode"] =!= 0 || !FileExistsQ[tmpFile] || FileByteCount[tmpFile] < 8,
    Print["Photoquick warning: Failed to read capture payload from ", port, " (", If[AssociationQ[res], res["StandardError"], res], ")"];
    Return[$Failed]
  ];

  rawBytes = ReadByteArray[tmpFile];
  DeleteFile[tmpFile];

  (* Parse 8-byte header: 4-byte ASCII magic 'PQ01', 4-byte uint32 sample rate *)
  magic = ByteArrayToString[rawBytes[[1 ;; 4]], "ASCII"];
  If[magic =!= "PQ01",
    Print["Photoquick warning: Unexpected header magic: ", InputForm[magic]];
    Return[$Failed]
  ];

  sampleRate = First @ ImportByteArray[rawBytes[[5 ;; 8]], "UnsignedInteger32"];
  rawCounts = ImportByteArray[rawBytes[[9 ;; All]], "UnsignedInteger16"];

  volts = N[rawCounts] * (OptionValue["VRef"] / OptionValue["ADCMax"]);
  timeAxis = N[Range[0, Length[volts] - 1]] / sampleRate;

  <|
    "Port" -> port,
    "SampleRate" -> sampleRate,
    "NumSamples" -> Length[rawCounts],
    "Duration" -> N[Length[rawCounts] / sampleRate],
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

(* -------------------------------------------------------------------------- *)
(* Display Flicker, Temporal Integration & Frame-Rate Aliasing Analysis       *)
(* -------------------------------------------------------------------------- *)

Options[PhotoquickFlickerAnalysis] = {
  "SmoothingRadiusMs" -> 0.25,
  "HysteresisFraction" -> 0.12
};
Options[iPhotoquickFlickerAnalysis] = Options[PhotoquickFlickerAnalysis];

PhotoquickFlickerAnalysis[flickerData_Association, opts: OptionsPattern[]] := Module[
  {v, lBlack, lWhite},
  v = flickerData["Volts"];
  {lBlack, lWhite} = Quantile[v, {0.05, 0.95}];
  iPhotoquickFlickerAnalysis[lBlack, lWhite, flickerData, opts]
];

PhotoquickFlickerAnalysis[blackData_Association, whiteData_Association, flickerData_Association, opts: OptionsPattern[]] := Module[
  {lBlack, lWhite},
  lBlack = Mean[blackData["Volts"]];
  lWhite = Mean[whiteData["Volts"]];
  iPhotoquickFlickerAnalysis[lBlack, lWhite, flickerData, opts]
];

PhotoquickFlickerAnalysis[lBlack_?NumericQ, lWhite_?NumericQ, flickerData_Association, opts: OptionsPattern[]] :=
  iPhotoquickFlickerAnalysis[N[lBlack], N[lWhite], flickerData, opts];

iPhotoquickFlickerAnalysis[lBlack_Real, lWhite_Real, flickerData_Association, OptionsPattern[]] := Module[
  {
    v, t, fs, span, expectedMean, overallMean, cycleBoundedMean,
    smoothN, vSmooth, mid, hyst, thHigh, thLow,
    state, risingIdx = {}, fallingIdx = {}, i, n,
    risingTimes, fallingTimes, allEdges, whiteDurationsMs = {}, blackDurationsMs = {},
    cyclePeriodsMs = {}, firstEdgeIdx, lastEdgeIdx,
    v10, v90, riseTimesMs = {}, fallTimesMs = {}, winSamples,
    seg, i10, i90, normMean, intErrV, intErrPct, aliasingQ
  },
  v = flickerData["Volts"];
  t = flickerData["Time"];
  fs = flickerData["SampleRate"];
  n = Length[v];
  span = Max[lWhite - lBlack, 10^-6];
  expectedMean = 0.5 * (lBlack + lWhite);
  overallMean = Mean[v];

  (* Light boxcar smoothing for robust edge detection without shifting phase *)
  smoothN = Max[1, Round[(OptionValue["SmoothingRadiusMs"] / 1000.0) * fs]];
  vSmooth = If[smoothN > 1, MovingAverage[ArrayPad[v, smoothN, "Fixed"], 2 * smoothN + 1], v];

  (* Use dynamic swing quantiles (3% and 97%) for edge timing & 10-90% rise/fall times,
     while keeping static LBlack & LWhite for temporal luminance integration *)
  {v10, v90} = Quantile[vSmooth, {0.03, 0.97}];
  mid = 0.5 * (v10 + v90);
  hyst = OptionValue["HysteresisFraction"] * Max[v90 - v10, 10^-6];
  thHigh = mid + hyst;
  thLow = mid - hyst;

  (* Schmitt-trigger state machine for noise-immune rising/falling edge finding *)
  state = If[First[vSmooth] >= mid, 1, 0];
  Do[
    If[state == 0 && vSmooth[[i]] >= thHigh,
      state = 1;
      AppendTo[risingIdx, i];
    ,
      If[state == 1 && vSmooth[[i]] <= thLow,
        state = 0;
        AppendTo[fallingIdx, i];
      ]
    ],
    {i, 2, n}
  ];

  risingTimes = t[[risingIdx]];
  fallingTimes = t[[fallingIdx]];

  (* Compute White and Black hold durations in milliseconds *)
  allEdges = SortBy[
    Join[
      Map[{#, "Rise"} &, risingIdx],
      Map[{#, "Fall"} &, fallingIdx]
    ],
    First
  ];

  If[Length[allEdges] >= 2,
    Do[
      If[allEdges[[i, 2]] === "Rise" && allEdges[[i + 1, 2]] === "Fall",
        AppendTo[whiteDurationsMs, 1000.0 * (t[[allEdges[[i + 1, 1]]]] - t[[allEdges[[i, 1]]]])];
      ];
      If[allEdges[[i, 2]] === "Fall" && allEdges[[i + 1, 2]] === "Rise",
        AppendTo[blackDurationsMs, 1000.0 * (t[[allEdges[[i + 1, 1]]]] - t[[allEdges[[i, 1]]]])];
      ],
      {i, 1, Length[allEdges] - 1}
    ];
  ];

  If[Length[risingTimes] >= 2,
    cyclePeriodsMs = 1000.0 * Differences[risingTimes];
  ];

  (* Compute cycle-bounded mean over an integer number of full cycles if >= 2 rising edges exist *)
  If[Length[risingIdx] >= 2,
    firstEdgeIdx = First[risingIdx];
    lastEdgeIdx = Last[risingIdx];
    cycleBoundedMean = Mean[v[[firstEdgeIdx ;; lastEdgeIdx]]],
    cycleBoundedMean = overallMean
  ];

  normMean = (cycleBoundedMean - lBlack) / span;
  intErrV = cycleBoundedMean - expectedMean;
  intErrPct = 100.0 * (cycleBoundedMean - expectedMean) / span;

  (* Estimate 10%-90% Rise Time and 90%-10% Fall Time across dynamic swing *)
  {v10, v90} = {v10 + 0.10 * (v90 - v10), v10 + 0.90 * (v90 - v10)};
  winSamples = If[Length[cyclePeriodsMs] > 0,
    Max[10, Round[0.35 * (Mean[cyclePeriodsMs] / 1000.0) * fs]],
    Min[Round[0.025 * fs], Floor[n / 4]]
  ];

  Do[
    If[idx > winSamples && idx + winSamples <= n,
      i10 = FirstPosition[Reverse[vSmooth[[idx - winSamples ;; idx]]], _?(# <= v10 &), None, {1}];
      i90 = FirstPosition[vSmooth[[idx ;; idx + winSamples]], _?(# >= v90 &), None, {1}];
      If[ListQ[i10] && ListQ[i90],
        AppendTo[riseTimesMs, 1000.0 * ((First[i10] - 1) + (First[i90] - 1)) / fs]
      ]
    ],
    {idx, risingIdx}
  ];

  Do[
    If[idx > winSamples && idx + winSamples <= n,
      i90 = FirstPosition[Reverse[vSmooth[[idx - winSamples ;; idx]]], _?(# >= v90 &), None, {1}];
      i10 = FirstPosition[vSmooth[[idx ;; idx + winSamples]], _?(# <= v10 &), None, {1}];
      If[ListQ[i90] && ListQ[i10],
        AppendTo[fallTimesMs, 1000.0 * ((First[i90] - 1) + (First[i10] - 1)) / fs]
      ]
    ],
    {idx, fallingIdx}
  ];

  (* Check for frame-rate / refresh-rate pulldown aliasing (frame-to-frame hold jitter > 10%) *)
  aliasingQ = If[Length[whiteDurationsMs] >= 3 && Length[blackDurationsMs] >= 3,
    (Max[whiteDurationsMs] / Max[Min[whiteDurationsMs], 0.1] > 1.10) ||
    (Max[blackDurationsMs] / Max[Min[blackDurationsMs], 0.1] > 1.10),
    False
  ];

  <|
    "LBlackVolts" -> lBlack,
    "LWhiteVolts" -> lWhite,
    "ExpectedMeanVolts" -> expectedMean,
    "MeasuredMeanVolts" -> cycleBoundedMean,
    "OverallMeanVolts" -> overallMean,
    "NormalizedMean" -> normMean,
    "IntegrationErrorVolts" -> intErrV,
    "IntegrationErrorPercent" -> intErrPct,
    "NumCompleteCycles" -> Max[0, Length[risingIdx] - 1],
    "MeanCyclePeriodMs" -> If[Length[cyclePeriodsMs] > 0, Mean[cyclePeriodsMs], Missing["NotAvailable"]],
    "EffectiveFlickerHz" -> If[Length[cyclePeriodsMs] > 0, 1000.0 / Mean[cyclePeriodsMs], Missing["NotAvailable"]],
    "ImpliedStimulusFps" -> If[Length[cyclePeriodsMs] > 0, 2000.0 / Mean[cyclePeriodsMs], Missing["NotAvailable"]],
    "WhiteHoldDurationsMs" -> whiteDurationsMs,
    "BlackHoldDurationsMs" -> blackDurationsMs,
    "MeanWhiteHoldMs" -> If[Length[whiteDurationsMs] > 0, Mean[whiteDurationsMs], Missing["NotAvailable"]],
    "MeanBlackHoldMs" -> If[Length[blackDurationsMs] > 0, Mean[blackDurationsMs], Missing["NotAvailable"]],
    "RiseTime10To90Ms" -> If[Length[riseTimesMs] > 0, Mean[riseTimesMs], Missing["NotAvailable"]],
    "FallTime90To10Ms" -> If[Length[fallTimesMs] > 0, Mean[fallTimesMs], Missing["NotAvailable"]],
    "AliasingDetected" -> aliasingQ,
    "Data" -> flickerData
  |>
];

PhotoquickFlickerDashboard[analysis_Association] := Module[
  {
    data, t, v, nShow, pWave, pHolds, whiteHolds, blackHolds,
    lB, lW, lExp, lMeas
  },
  data = analysis["Data"];
  t = data["Time"];
  v = data["Volts"];
  lB = analysis["LBlackVolts"];
  lW = analysis["LWhiteVolts"];
  lExp = analysis["ExpectedMeanVolts"];
  lMeas = analysis["MeasuredMeanVolts"];

  (* Show up to first 250 ms in waveform zoom panel *)
  nShow = Min[Length[t], Round[0.25 * data["SampleRate"]]];

  pWave = Show[
    ListLinePlot[
      Transpose[{1000.0 * t[[1 ;; nShow]], v[[1 ;; nShow]]}],
      PlotStyle -> Directive[RGBColor[0.12, 0.47, 0.71], AbsoluteThickness[1.2]],
      AxesLabel -> {"Time (ms)", "Signal (V)"},
      PlotRange -> {{0, 1000.0 * t[[nShow]]}, {0, 1.05 * Max[lW, Max[v[[1 ;; nShow]]]]}},
      PlotLabel -> StringTemplate["Waveform & Temporal Integration (Norm Mean = `` vs 0.500, Error = ``%)"][
        NumberForm[analysis["NormalizedMean"], {4, 3}],
        NumberForm[analysis["IntegrationErrorPercent"], {4, 1}]
      ],
      ImageSize -> 700
    ],
    Graphics[{
      {GrayLevel[0.5], Dashed, Line[{{0, lW}, {1000.0 * t[[nShow]], lW}}]},
      {GrayLevel[0.5], Dashed, Line[{{0, lB}, {1000.0 * t[[nShow]], lB}}]},
      {RGBColor[0.1, 0.65, 0.2], Dashed, AbsoluteThickness[2], Line[{{0, lExp}, {1000.0 * t[[nShow]], lExp}}]},
      {RGBColor[0.85, 0.15, 0.15], AbsoluteThickness[2], Line[{{0, lMeas}, {1000.0 * t[[nShow]], lMeas}}]}
    }]
  ];

  whiteHolds = analysis["WhiteHoldDurationsMs"];
  blackHolds = analysis["BlackHoldDurationsMs"];

  pHolds = If[Length[whiteHolds] > 0 && Length[blackHolds] > 0,
    ListPlot[
      {whiteHolds, blackHolds},
      Joined -> True,
      PlotMarkers -> Automatic,
      PlotStyle -> {RGBColor[0.95, 0.6, 0.1], RGBColor[0.2, 0.2, 0.2]},
      AxesLabel -> {"Frame #", "Hold Duration (ms)"},
      PlotRange -> {{0.5, Max[Length[whiteHolds], Length[blackHolds]] + 0.5}, {0, 1.25 * Max[Join[whiteHolds, blackHolds]]}},
      PlotLabel -> StringTemplate["Frame Hold Durations: Orange=White, Black=Dark (Aliasing: `` | t_rise=`` ms, t_fall=`` ms)"][
        analysis["AliasingDetected"],
        NumberForm[analysis["RiseTime10To90Ms"], {3, 2}],
        NumberForm[analysis["FallTime90To10Ms"], {3, 2}]
      ],
      ImageSize -> 700
    ],
    Graphics[{Text["Insufficient transitions detected for hold-duration plot", {0, 0}]}, ImageSize -> 700]
  ];

  GraphicsColumn[{pWave, pHolds}, Spacings -> 15, ImageSize -> 720]
];

(* -------------------------------------------------------------------------- *)
(* Stimulus Movie Generator (Full-Field, Checkerboard, Stripes)               *)
(* -------------------------------------------------------------------------- *)

Options[PhotoquickGenerateStimulus] = {
  "FrameRate" -> 24,
  "Duration" -> 10.0,
  "Resolution" -> {1920, 1080},
  "Pattern" -> "Checkerboard",
  "TileSize" -> 270
};

PhotoquickGenerateStimulus[outPath_String, OptionsPattern[]] := Module[
  {fps, dur, w, h, pat, tile, nFrames, frameA, frameB, frames, tmpDir, fA, fB, ffmpegBin, res},
  fps = OptionValue["FrameRate"];
  dur = OptionValue["Duration"];
  {w, h} = OptionValue["Resolution"];
  pat = OptionValue["Pattern"];
  tile = OptionValue["TileSize"];
  nFrames = Round[fps * dur];

  {frameA, frameB} = Switch[pat,
    "Checkerboard",
    {
      Image @ Table[N[Mod[Quotient[r, tile] + Quotient[c, tile], 2]], {r, 0, h - 1}, {c, 0, w - 1}],
      Image @ Table[N[1 - Mod[Quotient[r, tile] + Quotient[c, tile], 2]], {r, 0, h - 1}, {c, 0, w - 1}]
    },
    "Stripes",
    {
      Image @ Table[N[Mod[Quotient[r, tile], 2]], {r, 0, h - 1}, {c, 0, w - 1}],
      Image @ Table[N[1 - Mod[Quotient[r, tile], 2]], {r, 0, h - 1}, {c, 0, w - 1}]
    },
    _, (* "FullField" *)
    {
      Image[ConstantArray[1.0, {h, w}]],
      Image[ConstantArray[0.0, {h, w}]]
    }
  ];

  ffmpegBin = SelectFirst[{"/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"}, FileExistsQ, None];
  If[StringQ[ffmpegBin] && MemberQ[{"mp4", "mov"}, ToLowerCase[FileExtension[outPath]]],
    tmpDir = CreateDirectory[];
    fA = FileNameJoin[{tmpDir, "frameA.png"}];
    fB = FileNameJoin[{tmpDir, "frameB.png"}];
    Export[fA, frameA];
    Export[fB, frameB];
    res = RunProcess[{
      ffmpegBin, "-y",
      "-loop", "1", "-r", ToString[fps], "-i", fA,
      "-loop", "1", "-r", ToString[fps], "-i", fB,
      "-filter_complex",
      "[0:v][1:v]blend=all_expr='if(mod(N,2),B,A)',format=yuv420p",
      "-frames:v", ToString[nFrames],
      "-r", ToString[fps],
      "-fps_mode", "cfr",
      "-c:v", "libx264", "-crf", "10", "-g", "1", "-pix_fmt", "yuv420p",
      "-color_range", "pc",
      outPath
    }];
    DeleteDirectory[tmpDir, DeleteContents -> True];
    If[res["ExitCode"] == 0, Return[outPath]];
  ];

  frames = Table[If[OddQ[k], frameA, frameB], {k, 1, nFrames}];
  Export[outPath, frames, "FrameRate" -> fps]
];

End[];

EndPackage[];
