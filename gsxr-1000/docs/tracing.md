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

## 4. How this feeds the XDF
`traced.json` carries the RPM variable + scale, the lookup routines, the 48 resolved map inputs and
the traced constants. `make_gsxr_xdf.py` stamps a **“GSX-R TRACED INPUTS”** line onto each resolved
map and gives the traced constants real names. Regenerate with `extract_scalars.py` already run;
re-run `make_traced.py`-equivalent steps from the scripts above if you re-analyse.

## Open items
- Resolve the `gp` base to name the `gp-0x5bd2` rev-limit engage signal precisely.
- Extend input resolution beyond the 48 maps (deeper arg chasing in `DumpLookups.py`).
- Trace launch-RPM and the per-gear/speed limits from the same lookup + RAM-xref data.
