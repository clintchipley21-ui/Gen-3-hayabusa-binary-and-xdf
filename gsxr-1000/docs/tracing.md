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
