# GSX-R1000 M7 — function trace (from the GSX-R's own code + the manual)

This is the evidence trail for the headline variables and functions, traced from the GSX-R M7
binary itself (Ghidra, V850E3 core) plus the Suzuki service data, SDS-II list and ECM pinout — **not**
ported from the Hayabusa. Every claim below is backed by something checkable in the bin or the manual.

## Resources
- **Ghidra** headless, processor `V850:LE:32:default` (RH850 G3 core = V850E3), base `0x0`.
- Scripts (in `../tools` and the repo history): `DumpCalXrefs.py` (code→calibration refs),
  `DumpRam.py` (sensor-RAM refs), `DumpLookups.py` (resolve every call's args to C:const / M:ram),
  `DumpFunc.py` (decompile a named function).
- Manual: `GSX-R1000_2027_ServiceData`, `Specification`, `SDS-II DatabaseModelList`, ECM pinout
  (`SERVICE MANUAL_ECU-Pinout M7`).

## 1. Descriptor format and the lookup routines (proven)
The decompiled interpolation routines confirm the on-bin map descriptor layout exactly:
`FUN_000a201e` (2D) reads `*p`=type, `p[1]`/`p[2]`=col/row counts, `*(p+4)`/`*(p+8)`=X/Y axis
pointers, `*(p+0xc)`=data pointer, `*(p+0x14)`/`*(p+0x18)`=last-index caches, and does bilinear
interpolation (`FUN_000a1f60`/`FUN_000a1f9e`). `FUN_000a1fca` is the 1D variant. These two routines
account for 381 of the descriptor-carrying lookup calls.

## 2. Engine RPM variable and scale (proven)
`DumpLookups.py` resolved, for each map lookup, the RAM variable feeding its X axis (call arg 1).
Cross-referenced with the axis breakpoints in the bin:

- **`0xFEF02622` = engine RPM (primary).** It feeds the X axis of the 36-point maps at
  `0x150D48…` and is the most-referenced sensor RAM variable in the image (48 functions). Its paired
  X-axis breakpoints are round RPM values.
- **`0xFEF02E2C` = engine RPM (fuel/ignition control).** Its X-axis breakpoints are raw
  `2560,5120,7680,10240,12800,15360,17920,20480` = **1000,2000,…,8000 rpm** exactly.

→ **RPM scale: `rpm = raw / 2.56`** (equivalently raw = rpm × 2.56), established from the GSX-R's own
axis, and it matches the manual's idle of 1250 rpm (raw 3200). Other RPM-derived axes:
`0xFEF01E3E` (500–4000), `0xFEF0262C` (~800–3200). Throttle/load Y axis: `0xFEBF6169`.
Full list: `map-inputs.csv` (48 maps with their resolved X/Y variables).

## 3. Rev-limit cut (traced: `FUN_00064506`)
Decompiled logic (abridged), with `_DAT_fef02622` = engine RPM:

```
rpm   = _DAT_fef02622;
sig   = clamp(FUN_000a1b5c(*(gp-0x5bd2) - 0x8000) + 0x8000);   // derived RPM-domain signal
cut   = DAT_fef019e0 & 1;                                      // current cut state (hysteresis)
if (sig < DAT_00172ea6)            cut = 1;                    // 0x172EA6 ~ 13,155 rpm
else if (!cut) return;
if (DAT_00172ea8 < sig && DAT_00172eaa < rpm) cut = 0;         // 0x172EA8 ~ 14,933 rpm; 0x172EAA ~ 1,500 rpm gate
DAT_fef019e0 = cut ? (…|1) : (…&~1);                           // publishes the cut flag
```

Constants (identical in all four reads):

| Addr | Raw | ÷2.56 | Role (traced) |
|---|---:|---:|---|
| `0x172EA6` | 33678 | 13,155 rpm | soft/low rev-limit threshold |
| `0x172EA8` | 38229 | **14,933 rpm** | hard rev-limit threshold (matches the GSX-R1000 fuel cut) |
| `0x172EAA` | 3840 | 1,500 rpm | engine-running gate (RPM must exceed this) |

**Confidence:** the function reads engine RPM (`0xFEF02622`), gates on ~1,500 rpm, and the
`14,933 rpm` threshold is exactly where a GSX-R1000 M7 fuel cut sits — so these three addresses are
the rev-limit calibration. The engage path runs through a derived RPM-domain signal (`gp-0x5bd2`)
with hysteresis, so **confirm the exact cut point on a bench** before trusting it to the rpm.
These three are labelled in the XDF (folder "ZZ Decompiler-discovered scalars"), as is
the RPM-reading quickshifter/launch cut `FUN_0002c8fe` (QS maps `0x1512e8`/`0x1512d4`).

## 3b. Variable dictionary (axis inputs traced from the code)
Resolving the two lookup routines' call arguments — and, once `gp = 0xFEBFC000` was known (see 3c),
setting it as context so gp-relative sdata accesses resolve too — linked **374 of the 791 maps** to
the RAM variable feeding each axis. Classifying those variables by their axis breakpoints
(rpm = raw/2.56) gives the dictionary in **`variables.csv`** — 74 variables. Highlights:

| RAM | Role (from axis shape) | Evidence |
|---|---|---|
| `0xFEBF637E` | **engine RPM (main map axis)** | the X axis of **95 maps**; breakpoints 1000…12000 rpm |
| `0xFEBF6436` | **main load axis (airflow/TP)** | the axis of **85 maps** |
| `0xFEF02622` | engine RPM (primary sensor) | most-referenced sensor var (48 fns); RPM-stepped axes |
| `0xFEF02E2C`, `0xFEBF615E` | engine RPM (control / sub-range) | axes 1000…14000 / 1000…9000 rpm |
| `0xFEBF63C8`, `0xFEBF60F4`, `0xFEBF63FA`, `0xFEF02D8A` | engine RPM (high range) | 12800–14000 rpm (limiter region) |
| `0xFEBF6169`, `0xFEBF62CC`, `0xFEBF60C0`, `0xFEF00DB2` | throttle / load | raw 0…255, RPM×load Y-axes |
| `0xFEF0267D` | gear / mode index | axis 0…10 |
| `0xFEBF5E7A`, `0xFEF028xx`, `0xFEBF637C` | signed sensor (lean/pitch/rate, centred 0x8000) | — |

Each of the 374 maps carries a **“GSX-R TRACED INPUTS”** line in the XDF; the full list is
`map-inputs.csv`, the machine-readable form is `traced.json`.

## 3d. Launch control (traced)
Decompiling the launch cluster shows the GSX-R1000 launch limits **throttle per gear**, not a fixed
RPM hold:

- `FUN_0002862a` — post-launch RPM margin, 1D lookup on map `0x1511C4`, indexed by RPM.
- `FUN_000286b6` — release phase-out duration, 2D lookup on `0x1511D8` (launch counter × speed),
  gated by the launch-active flag.
- `FUN_000286f4` — launch state machine: sets/clears the active flag and runs the release counter
  (`fef0030c`).
- `FUN_0002885e` — launch timer/debounce: counts `fef0031a` up to threshold **`0x154CF6` (= 13)**.
- Active flag: `0xFEBF5E6A` bit 3 (`gp − 0x6196`).

The actual launch *limit* is the per-gear **“Launch Control – Throttle Limit | Gear 2…6/Neutral”**
maps (`0x174FB0`–`0x175020`, `0x18E6D8`) — already in the XDF. So there is no single “launch RPM”
scalar to tune; raise/lower launch aggressiveness via those throttle maps. The timer constant
`0x154CF6` is named in the XDF.

## 3e. Traction control (traced)
`FUN_00055016` is the TC controller. It reads the **TC level byte `0xFEBF6459`** (`gp − 0x5ba7`,
value 1–10) and switches on it to select that level's map set — level 1 → `0x168550`, level 2 →
`0x168608`, … level 10 → `0x168bc8` — which is **exactly** the ported `TC - Cut vs Slip Error |
Level N` descriptor addresses, so the TC map labelling is validated against the code. Each set has
Cut-vs-**Slip Error** / **Slip Rate** / **Slip History** maps, all indexed by the **slip variable
`0xFEBF6164`**, plus a per-level threshold array at `0x1701EC…0x170200` (u16/level) and a slip gate
`0x1701E4`. Full decompile in `trace-tc.c`.

So to tune TC: the 10 levels are the `TC -` maps already in the XDF; `0xFEBF6459` is the live level
and `0xFEBF6164` the live slip (both now named in every map's TRACED INPUTS line).

## 3f. Downshift auto-blip / engine-brake throttle (traced)
The GSX-R1000 opens the ETV on a closed-throttle downshift/decel through the **engine-brake throttle
controller**, not a separate quickshifter-blip map:

- `FUN_00028de0` (dispatcher) → `FUN_00028ca6` (EB throttle controller) write the ETV throttle-opening
  demand **`0xFEF005C0`**.
- On decel/downshift entry it applies the **decel-entry blip map `0x151210`** ("Engine Brake Control
  :: Throttle Opening … neutral/clutch/decel-entry") for a duration — a counter `fef00526` runs up to
  **`0x154E16` (= 25 counts, the blip duration)**, mode `0x154E17`.
- Once engine-braking proper, it uses the **EB-Level 1/2/3 throttle-opening maps** `0x15122C` /
  `0x151248` / `0x151264` (RPM × gear), indexed by RPM `0xFEF0262C` and gear.
- Shift detection that triggers it: `FUN_0002a2ba` reads the GP-sensor low/high thresholds
  `0x150ED8`/`0x150F48` (or `0x150EA0`/`0x150F10`, mode `fef0267f`) vs RPM × gear.

So to tune the downshift blip / engine-braking throttle: the opening amounts are the **Engine Brake
Control :: Throttle Opening** maps (already in the XDF) and the entry blip is `0x151210` + duration
`0x154E16`; the live demand is `0xFEF005C0`. Decompile in `trace-engine-brake-blip.c`.

## 4. How this feeds the XDF
`traced.json` carries the RPM variable + scale, the lookup routines, the 48 resolved map inputs and
the traced constants. `make_gsxr_xdf.py` stamps a **“GSX-R TRACED INPUTS”** line onto each resolved
map and gives the traced constants real names. Regenerate with `extract_scalars.py` already run;
re-run `make_traced.py`-equivalent steps from the scripts above if you re-analyse.

## 3b-ii. Sensor variable block (title-anchored, contiguous in sdata)
Cross-referencing each traced input against the ported map title that names its axis
(`vs RPM x TP`, `x Gear`, `vs ECT`, …) pins the core sensor variables — and they fall in one
contiguous `0xFEBF64xx` sdata array, which corroborates them:

| RAM | Sensor | Maps anchored |
|---|---|---|
| `0xFEBF637A`, `0xFEBF637E` | engine RPM (map axis) | 32+ |
| `0xFEBF6436` | **IAP / intake pressure** (main load axis) | 85 |
| `0xFEBF6440` | **ECT** engine coolant temp | 23 |
| `0xFEBF6442` | **gear position** | 17 |
| `0xFEBF6443` | **IAT** intake air temp | 1 |
| `0xFEBF63C4`, `0xFEBF63C0` | **TP** throttle position | 13 |
| `0xFEBF6394` | barometric pressure | 2 |
| `0xFEBF6164`, `0xFEBF60F4` | traction-control slip | 2 |

These names flow into every map's `GSX-R TRACED INPUTS` line (so even some generic curves now read
`X = gear position`, etc.). The `0xFEF02622`/`0xFEF02E2C` RPM sensor variables (section 2) sit in the
other sensor RAM bank.

## 3c. gp base resolved → rev-cut engage signal named
The V850 global pointer is set in crt0, disassembled directly from the image:

```
0x10C7C  mov 0xFEBFCD20, sp
0x10C82  mov 0xFEBFC000, gp      <-- gp = 0xFEBFC000
0x10C88  mov 0x00148000, tp
```

So the rev-cut engage signal `*(gp − 0x5BD2)` = **`0xFEBF642E`** — an RPM-domain value sitting in the
`0xFEBF6xxx` sdata sensor block right next to the traced RPM axis variable `0xFEBF615E` and the load
axis `0xFEBF6169`. That confirms `FUN_00064506` compares an RPM signal against the two thresholds and
gates on engine RPM `0xFEF02622` > ~1,500 rpm — i.e. the rev limiter, end to end.

## Open items
- Extend input resolution past 62 maps (more lookup routines: `0x118b0`, `0xa2344`; inlined lookups;
  now that `gp = 0xFEBFC000` is known, gp-relative axis inputs can be resolved too).
- Launch-RPM: the per-gear launch throttle-limit maps are present (ported, HIGH); the launch RPM
  hold value is a scalar not yet isolated from the clutch/mode gating.

## 3g. SDMS power-mode selector + cruise/speed-governor code (traced)

**Power mode (SDMS drive mode).** The drive-mode level is the byte **`0xFEF0267D`**, range **0–10**.
A dedicated switch controller cluster (`0x07BEF–0x07D9`, matched `ld.bu`/`st.b` pairs) reads, latches and
writes it — i.e. the mode-button debounce/state. `FUN_00029198` (`0x29198`) loads it as the **index into
the 11-point mode-gain curve `0x1513B0`** and scales the electronic-throttle target: the 2D target map is
`0x1511A8` (16-bit, 23×39, X = rider demand `0xFEF00530`, Y = engine RPM), with a 1D fallback curve
`0x150BCC` (36 pts) when `FUN_00028EE4 != 0`. The identity is self-confirming: the curve `0x1513B0`'s own
ported axis is labelled **"SDMS Field-3 Level (0–10)"** and its breakpoints are exactly 0..10 — the same
range the mode byte takes. This is the A/B/C-equivalent power level on the GSX-R1000R M7. Per-level gains
are in `0x1513B0`; verify on a bench.

**Cruise / speed-governor.** The M7 image carries Suzuki's **speed-governor (cruise) calibration and code**
even though the GSX-R1000R has no cruise switch — shared platform code (the GSX-S1000/GT siblings run
cruise). `FUN_0002DA0E` (`0x2DA0E`) computes set-speed tracking from the accel-rate-gain curve `0x150DAC`
and the **speed-correction-vs-set-speed table `0x150E5C` (14 pts, 30–240 km/h)**; `FUN_0002E0AE` ramps the
governor target (curves `0x150DD4/0x150DE8/0x150DFC/0x150E10`, scale denominator `0x154D8C` = 161); and the
state machine `FUN_0002D95E` (`0x2D95E`) drives the governor state byte **`0xFEF005F8`** (codes
0x0B/0x0E/0x11/0x12) gated by the mode byte `0xFEF00652`. The set-speed enable gates are `0x154D6E` /
`0x154D70` (raw 640). **Confidence: low that this is live on the GSX-R1000R** — the labels are ported from
the cruise-capable map set; treat it as "speed-governor code present", not a confirmed working feature.

## 3h. Quickshifter upshift ignition-cut (traced)

The upshift cut is the spark-side mirror of the downshift auto-blip (§3f). Traced end to end:

- **Master enable `0x154DD2`.** The QS dispatcher `FUN_0002B720` runs the whole quickshifter pipeline
  **only while `0x154DD2 == 0`** (stock 0 = enabled). When non-zero it resets every QS output
  (`DAT_febf5e8d = 0x40`, `fef005f2 = 0xFFFF`, the ETV reset `*(gp−0x618A) = 0x100`). This is the
  one byte that turns the quickshifter off.
- **Detection `FUN_0002A96E` (`0x2AA62`).** Arms the cut when the gear-position (GP) sensor
  (`gp−0x5C86`) crosses from the **Window-B offset curve `0x1509A8`** up past the **Window-C curve
  `0x1509BC`**, with the shift signal `0xFEF02630` inside the valid window `0x1559BC..0x1559BA` (×64)
  and gears 1–2 excluded. It latches the cut-state flags in **`0xFEF005A3`** (bit0 armed, bit2
  cut-active) and calls the cut actuator `FUN_00029F22`. Arming thresholds: `0x154C7C`=2,
  `0x154C7E`=23; armed-mode bytes `0x154DD4/0x154DD5`=0x80.
- **Phase sequencer `FUN_0002A698` (`0x2A6E8`).** Steps the cut through phases 1–4 in byte
  **`0xFEF005F6`**, which selects the 3-phase ignition-retard maps `0x15234C` / `0x1523BC` / phase-3
  (retard vs RPM × TP) — the maps already carried as *Quickshifter :: Upshift Ignition Retard Phase 1/2/3*.
- **Window target `FUN_0002A652` (`0x2A696`).** Builds the per-gear window threshold `fef00570` from
  base `febf5e78` + the per-gear offset curve `0x15096C`.

So the full upshift path is: *master-enable → GP-sensor window detect → arm flags → phase sequencer →
3-phase ignition retard → cut actuator*. Tune feel via the Phase 1/2/3 retard maps and the window
offset curves; disable with `0x154DD2`. Decompile in `docs/trace-upshift.c`.

## 3i. Idle air-control (traced)

The idle system is the ECT-indexed airflow/target curve set (base airflow `0x170558`, target A/B
`0x170870`/`0x1708B0`, ECT curves `0x1708F0..`) driven by a closed-loop corrector:

- `FUN_00053DC6` gates the correction on a ready-flag mask (byte `gp−0x5ED6`); the whole
  airflow-correction block is skipped when the **enable byte `0x1702C0` == 0x80** (stock `0xFF` = active).
- `FUN_00053C0C` runs the feedback step with a **debounce count `0x1702C1` = 13**.
- `FUN_00053F3E` keeps a moving average of the airflow/slip signal `0xFEBF6166` over a window of
  **`0x1744AE` = 3** samples (clamped ≤19).
- `FUN_0004FF2E` is the per-channel servo update; feedback state lives in `0xFEF00F48/0xFEF00F49`.

The idle *target* is the ported ECT curves; these three scalars gate and tune the closed loop.

## Efficient re-tracing workflow (persistent Ghidra project)

Earlier traces each re-imported the 2 MB image and re-ran full auto-analysis (~6 min/run). That
analysis is identical every time, so it is now done **once** and reused:

```
# one-time (~5 min): import + analyze, keep the project (no -deleteProject)
analyzeHeadless ./proj gsxrAll -import gsxr_48L00.bin -processor V850:LE:32:default \
  -loader BinaryLoader -loader-baseAddr 0x0

# every subsequent dump (~8 s): reopen WITHOUT re-analysis, batch-decompile a function list
analyzeHeadless ./proj gsxrAll -process gsxr_48L00.bin -noanalysis \
  -scriptPath . -postScript DumpFunc.py 52a2c,52f74,53c2e,...  out.c
```

Measured: **~8 s** to decompile a batch of ~11 functions vs ~6 min before — same decompiler, same
output, ~45× faster. `DumpRam2.py <out> <LO> <HI>` sweeps any RAM window for cross-references the
same way. This is the tool for extending the trace further.

## Coverage ceiling (map inputs)

`GSX-R TRACED INPUTS` is resolved for **378 / 791** maps. Of the rest, ~199 cite a reader function
but index their lookup with a **computed expression** (not a direct sensor read), and the balance are
read through inlined interpolation. Neither can be attributed to a single input variable at the same
confidence as the sensor-block-anchored 378, so they are intentionally left unlabelled rather than
filled with low-confidence guesses. Raising this number further means reading each reader's decompile
by hand (now cheap via the workflow above) — accurate, but per-map manual work.

## 3j. Why map-input coverage stops at 378/791 (three methods, all validated)

With the fast persistent-project tooling (above) I tried to resolve the ~326 remaining maps that cite
a reference but carry no input, **validating each method against the 378 already-traced maps as ground
truth**. All three fall short of that accuracy bar, so the tail is left unlabelled rather than guessed:

1. **Lookup-argument grouping.** Pair each map-descriptor pointer with the RAM var in the same
   interpolator call. Result: the 326 tail maps are **never** passed to the dispatched interpolators
   `a1fca`/`a201e` — only 6 descriptors appear there and all 6 are already resolved. The tail is read
   through other helpers or open-coded indexing.
2. **Decompile call-parsing.** Batch-decompile all 70 distinct reader functions (one ~100 s pass) and
   parse each `FUN_…(&DAT_00<desc>, <index>)` call, back-tracing the index to a sensor via
   `gp = 0xFEBFC000`. Result: the tail descriptors' addresses **do not appear as a call argument** in
   their reader's C — the access is open-coded (computed base register Ghidra never folds to the
   constant), and several cited "readers" are small flag-setters that don't do the lookup at all.
3. **Axis-domain classification.** Classify each map by its own (GSX-R) axis breakpoints/units and map
   the domain to the GSX-R-traced sensor var. Validated against the 378: **46 % domain precision**
   overall — good for explicitly-RPM axes (**88 %**) but **0 %** for °C and gear-bit axes, because the
   real inputs there are frequently *derived* signals (e.g. `0xFEF0262C`, an RPM-domain intermediate),
   not the raw sensor the axis unit implies.

**Conclusion.** 378 (sensor-block-anchored, call/gp-traced) is the reliable ceiling for *named input
variables*. For the remaining maps the input **domain** is already carried by the map title and axis
(e.g. *"… vs RPM × TP"*, *"… vs ECT"*), which is accurate; only the exact RAM variable is
undetermined, and assigning one automatically would be ~50 % wrong. Raising the number further is
per-map manual decompile reading — now cheap via the workflow above, but not safely automatable.

## 3k. Per-family reader decompiles — coverage raised 378 → 575

§3j showed bulk automation can't resolve the tail accurately. The accurate-and-fast route is the
persistent-project workflow applied **per subsystem**: pull each family's reader functions from the
cal-xrefs, batch-decompile them (~8–100 s), and read the gp-relative sensor in each lookup call. Done
for four families the user prioritised:

- **Fuel (+21).** Readers in `docs/trace-fuel.c`: decel-cut/recovery (ECT `0xFEBF6440`), per-gear
  enrichment/trim (RPM `0xFEBF637A` × TP), air-charge main (TP `0xFEBF63C4` × RPM), EB fuel-cut
  (speed `0xFEBF63F6` × gear), baro corrections (`0xFEBF6394`).
- **Ignition (+32).** `docs/trace-ignition.c`: throttle/second thresholds (RPM axis `0xFEBF615E`),
  dwell (battery `0xFEBF638C` × RPM), transient rate curves (RPM), Trim A–D + mode maps
  (TP `0xFEBF63C2/63C6` × RPM), per-gear retard (TP × RPM), EB ignition trim (`0xFEF0262C` × gear).
- **Traction control (+129).** `docs/trace-tc-controller.c`: `FUN_00055016` gives the per-level block
  order — Cut-vs-Slip Error (slip `0xFEBF6164`) / Rate (`0xFEBF60F4`) / History (`0xFEBF63FA`) / Lean
  Gain (lean `0xFEBF6430`); target-slip reader (`0xFEBF5E7A`), slip-gain reader (RPM `0xFEBF637E`).
- **ETV / cruise / anti-lift (+15).** `docs/trace-etv.c`: ETV monitor (IAP `0xFEBF6436` × RPM),
  ETV gain (RPM `0xFEBF637C`), cruise correction (computed speed error vs `0xFEBF5E86`), LF
  throttle-limit (demand `0xFEF02E2C` × load `0xFEBF6169`).

**Now 575 / 791.** Every entry is a gp-relative sensor read in the map's own lookup call — same
confidence as the original 378. What's still unresolved is genuinely pointer-table-selected (the 42
`ETV-PWR/Slot` power-mode maps via table `0x192BC0`, the advance-timing and ride-mode ECT-retard
maps) or small inline curves — these have no single decompilable reader, so they stay unlabelled
rather than guessed.

## 3l. Power-mode (PWR/Slot) ETV maps — pointer-table dispatch resolved (+42 → 617)

The 42 `ETV - PWR`/`ETV - Slot` maps §3k left unresolved are pointer-table selected, so they needed
the dispatcher traced rather than a direct reader. `FUN_0008BE2C`:

```
_DAT_fef02e0c = (&PTR_DAT_00192ba8)[ gear(fef02e51)*6 + mode(fef0267c) ];   // pick the map
_DAT_fef02e26 = a201e(_DAT_fef02e0c, _DAT_fef02e44, _DAT_fef02e46);         // interpolate it
```

`FUN_0008BDC8` sets the two axis values: `_DAT_fef02e44 = *(gp−0x5c52)` = **`0xFEBF63AE`** (rider
throttle demand / APS) and `_DAT_fef02e46 = *(gp−0x5c84)` = **`0xFEBF637C`** (engine RPM); `fef02e51`
is the gear (bitmask→0..5) and `fef0267c` the power-mode column — these only choose *which* map, not
the axes. So every PWR/Slot map shares **X = APS `0xFEBF63AE` × Y = RPM `0xFEBF637C`**
(`docs/trace-pwr.c`). Map-input coverage is now **617 / 791**; the remainder are advance-timing
per-cyl, ride-mode ECT-retard and small inline curves with no single decompilable reader.

## 3m. Global sweep — every code-read map resolved (655/791)

A final pass decompiled **every** function that references an as-yet-unresolved descriptor (46
functions) and bound descriptor→input two ways: (a) direct `&DAT`/pointer-var first argument to an
`a1fca`/`a201e`/`a2344` call, and (b) for table-dispatched maps, the reader function's **single
consistent** lookup-index signature (the table only selects the map; the axes are fixed gp reads).
Both are code facts, not guesses; functions with more than one index signature were skipped rather
than guessed (none occurred).

**Final coverage: 655 / 791.** The 136 remaining are **not sensor-indexed calibration maps**: 5 are
ASCII hardware-ID strings, and ~131 are regions the code reads by raw/computed indexing (data tables,
counters, ID/compare blocks) with no interpolated sensor axis — there is no X/Y input to report, so
they are left without a `GSX-R TRACED INPUTS` line rather than given a fabricated one.

## 3n. Diagnostics, MIL lamp, and CAN/meter outputs

**Diagnostic monitors — traced (calibration).** The OBD monitors are real functions and their
enable/threshold calibration is now named:
- **HO2 / catalyst O2 monitor** — `FUN_00040BAC` (completion threshold `0x155AB2`) and `FUN_0003F8B2`
  (reference voltages `0x155A62`/`0x155A64`); baro-correction enable window `0x170216/0x170218/0x17021A`
  (`FUN_0005721A`).
- **ETV Level-2 torque/air safety monitor** — `FUN_0008AE3E`/`FUN_0008E3B8`, output clamp
  `0x192CEA`/`0x192CEC`, plus the `0x193xxx` air/torque-estimate maps (IAP × RPM, already input-traced).
- **EVAP purge monitor** and the **wheel/speed monitor** are present with their maps.

**MIL / warning lamp — NOT individually decoded (deliberately).** The lamp is driven through the
RH850 port I/O space (`0xFFFF_xxxx` register writes — 1008 such refs in the image) by logic that
aggregates the monitor-result flags. Pinning the exact port bit for the MIL needs the specific RH850
variant's port datasheet, which isn't in hand, so no lamp bit is labelled — labelling one would be a
guess. The upstream monitors that *would* light it are the ones named above.

**CAN / meter (dash) outputs — NOT individually decoded (deliberately).** The instrument-cluster
frames (tach, coolant, gear, warning lamps) are assembled in code and written to the RS-CAN peripheral
(`0xFFE6_xxxx` / `0xFFC6_xxxx`). The only calibration in this path is the **Meter Fuel Consumption
RPM/IAT scaling** (in the XDF). Decoding individual CAN frame fields needs the Suzuki CAN DBC, which
isn't in hand, so no CAN field is labelled.

Bottom line: the diagnostic **monitors** are calibration and are covered; the **MIL lamp** and **CAN
dash output** are peripheral/logic with no per-bit calibration, so they're documented but not
fabricated into fake maps or flags.
