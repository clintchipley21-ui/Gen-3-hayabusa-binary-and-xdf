# Gen 3 Hayabusa — binaries and XDFs

Suzuki Hayabusa Gen 3 (2022+, Renesas RH850/E1L). TunerPro XDFs, stock 2 MB reads, and a custom
"race software" build that adds speed-density fuelling on a 3-bar MAP sensor, boost spark retard and
rolling anti-lag.

> **Everything here is unverified on hardware.** Bench an ECM first and keep a stock read for recovery.

> **Sibling model:** [`../gsxr-1000/`](../gsxr-1000/) holds four Suzuki GSX-R1000 (M7) reads and TunerPro
> XDFs for them. The GSX-R uses the same ECU family, the same map-descriptor format and the same
> field-1 CRC, so its XDFs were built by porting these Hayabusa map definitions onto the GSX-R's own
> descriptors (confidence-tagged). See [`../gsxr-1000/README.md`](../gsxr-1000/README.md).

## Where to start

| I want to… | Use |
|---|---|
| Flash the current race build | [`race/Busa-SD-v4.1.bin`](race/) |
| Edit the race build in TunerPro | [`race/Busa-SD-v6.xdf`](race/) |
| Edit a stock read | Open `stock/<software>/` for your read (for example `stock/5JCZSJ40/`): it holds the `.bin` and its matching `.xdf` |
| Add anti-lag / air-shifter to a stock bin | `python3 tools/apply_patches.py stock.bin out.bin` (see [`race/`](race/)) |
| Fix the checksum after editing | `python3 tools/fix_field1_crc.py tuned.bin` |

## Layout

```
race/                  custom speed-density + anti-lag build (see its README)
  Busa-SD-v4.1.bin     current race bin
  Busa-SD-v6.xdf       race XDF v6 for it
  notes/               change list for every SD version, SD-v1 to SD-v4.1
  als/                 anti-lag assembly source and simulator harness
  old/                 SD-v1 to SD-v4 bins and the XDFs that went with them (SD-v2 to SD-v5, test26)
stock/
  <software>/          one folder per stock read, e.g. 5JCZSJ40/: 5JCZSJ40.bin and 5JCZSJ40.xdf
  other/               reads from other software families (see below)
  master/              master-v9.xdf (full-length master the per-read XDFs are built from), v9-notes.txt
  master/old/          stock XDFs v2 to v8 (there is no v6)
re/                    Ghidra project and decompiled C for 5JCZSJ40
docs/                  xdf-notes.csv (full text of every XDF item), function-names.csv (readable names
                       for decompiled functions) and function-registry.csv (every FUN_ referenced),
                       ram-variables.csv, dtc-table.csv, v5-index.csv, autodef-trace.csv
tools/                 fix_field1_crc.py, apply_patches.py, make_stock_xdfs.py, make_race_xdf.py,
                       xdf_userfriendly.py, xdf_patches.py, xdf_funcnames.py, xdf_corrections.py,
                       xdf_autodef_trace.py
```

All paths are kept short (at most 27 characters inside the repo) so the folder can be copied into Dropbox
or a Windows folder without hitting path-length limits.

## Stock reads

Each folder in `stock/` holds one unmodified 2 MB read and the XDF built for it. All eight reads have
byte-identical code (0x10000–0x14FFFF) and a valid field-1 CRC. Every byte that differs between them lies
inside an item the XDF defines (apart from an ID string and one variant word, which the XDFs add), so map
descriptors, addresses and sizes are the same in all of them.

Each XDF has 758 tables, 2,769 constants and 195 flags. The VALUES / STOCK line in every description is that
read's own value, and items whose data differs from 5JCZSJ10 are marked "DIFFERS FROM 5JCZSJ10".

**Folders.** Every XDF you open in TunerPro (the eight stock ones and the race XDF) uses the same folders.
TunerPro's Parameter Tree nests them, so related folders sit under a parent:

| Parent | Child folders |
|---|---|
| Fuel | 01 Main Fuel Maps, 02 Strategy/Blend/Settings, 03 Injectors, 04 Start/Warm-Up/Air Temp/Baro, 05 Accel Enrichment & Decel Cut, 06 Closed Loop (O2) |
| Ignition | 07 Base Advance Maps, 08 Trims and Corrections |
| Throttle & Ride Modes | 09 Throttle (ETV) & Power Modes, 10 Ride Mode Presets |
| Limiters, Launch & Shift | 11 Limiters, 12 Launch Control, 13 Quickshifter |
| Traction & Chassis | 14 Traction Control, 15 Anti-Lift/Pitch/Engine Brake, 17 IMU/Wheel Speed/Gear |
| Cruise & Idle | 16 Cruise Control, 18 Idle & Cooling Fan |
| Sensors, ECU & IDs | 19 Sensors & Scaling, 40 ECU Settings, 41 ETV Safety Monitor, 99 IDs/Variant/Checksums |
| Diagnostics | 30 DTC On/Off, 31 DTC Thresholds & Lamp, 32 OBD/CAN/Meter/EVAP |
| (top level) | 20 Race, 22 Patches & Air-Shifter |

Each item's first folder is its home; the cross-cutting views **00 Start Here**, **80 Low Confidence**,
**88 All Switches** and **89 Unused / Flat** appear nested under it as well (so, e.g., a key fuel map shows
up under both `Fuel → 01 Main Fuel Maps` and `… → 00 Start Here`).

**Function names.** Where a decompiled routine has been identified, its `FUN_<addr>` handle in the item
descriptions is replaced with a readable name (e.g. "per-gear RPM limiter", "front wheel-speed calc");
unidentified ones keep `FUN_<addr>`. The name list is `docs/function-names.csv` (edit it to add names) and
`docs/function-registry.csv` lists every function referenced with its name or "unidentified".

**TunerPro limits.** The SD-v5 race XDF crashed TunerPro on open because of its long, multi-line header. The
XDFs here keep a single-line header (under 480 characters) and **short item descriptions (at most 420
characters, about 210 on average)**: what the item does, this bin's value, a confidence / "differs" tag and
its address. Descriptions take about 0.8 MB per file, down from 1.6 MB. The full text of every item (how the
ECU uses it, axes, tuning notes, the code it was traced through) is in
[`docs/xdf-notes.csv`](docs/xdf-notes.csv): search it by title or address. The stock master in
`stock/master/` keeps the full text inline and may be too large for TunerPro, so treat it as reference.
Regenerate with `python3 tools/make_stock_xdfs.py`, `python3 tools/make_race_xdf.py` and
`python3 tools/xdf_userfriendly.py` (notes CSV) after changing the master.

Calibration bytes differ from 5JCZSJ40 by the amounts below.

| Folder | ECM part | Software | Calibration bytes different from 5JCZSJ40 |
|---|---|---|---|
| [`5JCZSJ00/`](stock/5JCZSJ00/) | 32990-10L0 | 5JCZSJ00 | 22 |
| [`5JCZSJ10/`](stock/5JCZSJ10/) | 32990-10L1 | 5JCZSJ10 | 1,032 (stock v9 XDF verified on this read) |
| [`5JCZSJ20/`](stock/5JCZSJ20/) | 32990-10L2 | 5JCZSJ20 | 5 |
| [`5JCZSJ30/`](stock/5JCZSJ30/) | 32990-10L3 | 5JCZSJ30 | 1,029 |
| [`5JCZSJ40/`](stock/5JCZSJ40/) | 32990-10L4 | 5JCZSJ40 | — (base for every SD bin) |
| [`5JCZSJA0/`](stock/5JCZSJA0/) | 32920-10LA | 5JCZSJA0 | 18 |
| [`5JCZSJB0/`](stock/5JCZSJB0/) | 32920-10LB | 5JCZSJB0 | 123,307 |
| [`5JCZSNC0/`](stock/5JCZSNC0/) | 32920-10LC | 5JCZSNC0 | 252 |

`stock/other/` holds files the XDFs here do **not** fit:

- `5JCXSJ10.bin` — software 5JCXSJ10, from the original DanCycles HayabusaGen3 project
  (see [NOTICE.md](NOTICE.md)). Roughly 700 KB of code differs from 5JCZSJ10, and the field-1 CRC method
  below does not match it.
- `5JCUSJ40.ori` (ECM 32990-10L4) — software 5JCUSJ40 in a 2,031,679-byte container, not a plain 2 MB read.

## Race-relevant settings (stock XDFs, no code patch)

| Setting | Where in the XDF | Stock |
|---|---|---|
| Top-speed limiter (~299 km/h) | `Per-Gear Limiter \| 6th` — a 6th-gear RPM limit, enable 0x15444B | 10,450 soft / 10,550 rpm hard |
| Per-gear rev limits 3rd–5th | `Per-Gear Limiter \| 3rd/4th/5th` | parked at 25,000 rpm (off) |
| Quickshifter cut strategy | `Quickshifter :: Shift Actions` (checkboxes: spark cut, retard, fuel cut + throttle, fuel factor per phase, on- and off-throttle) | see each read's XDF |
| Launch control RPM | `Launch Control \| Level 1-3` and `Launch Control - Throttle Limit` | Level 1 hard cut 3,700 rpm |

## Code patches (add a feature to a stock bin)

Two code patches can be added to a stock bin, and the XDF folder `22 Patches & Air-Shifter` holds the
settings for both:

- **Rolling anti-lag** — the SD-v4.1 anti-lag on a stock bin.
- **Auto-upshift (air-shifter)** — at a per-gear RPM target, pulses the PAIR-valve output to drive
  a relay → MAC valve → air ram (no spark cut; the factory quickshifter does that).

Apply them with `python3 tools/apply_patches.py stock.bin out.bin` (both), or add `antilag` / `autoshift`
for one — it checks the bytes and re-stamps the CRC. Then open the result in its XDF and enable/tune in the
`22 Patches & Air-Shifter` folder. (The patches are applied by the script, not from inside TunerPro — the
native TunerPro patch element crashed TunerPro on open, so it is not embedded.)

Both ship **disabled** and are **unverified on hardware**. Details and the required bench check for the
air-shifter output are in [`race/`](race/) and [`race/notes/autoshift.txt`](race/notes/autoshift.txt).

## XDF accuracy (v9.2 audit)

Every RAM variable the XDFs use for units was re-checked against the code that writes it, every constant
against the code that compares it, and every table against the ECU's own map descriptors. Five variables
had been mislabelled (two wheel speeds shown as throttle position, throttle rate shown as throttle position,
traction-control slip error shown as grip %, a wheel-derived RPM shown as engine RPM), which put wrong
units on about 120 items. All are fixed in the stock and current race XDFs; details and the method are in
`stock/master/v9-notes.txt` and `tools/xdf_corrections.py`.

v9.3 traced every auto-defined constant through the decompiled code: each one's title and description now say
what the code does with it (threshold on which signal, debounce count, switch, filter strength...) with a
confidence level and the line of code. The full trace is `docs/autodef-trace.csv`. Notably **0x1824C6 is a tip-in rate
gate (1.41 deg / 4 samples), not a 91.4 deg WOT gate.**

## Checksums

- **Field 1**: CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF) over 0x10000–0x1FFAFB, stored big-endian at
  0x1FFAFE. Re-stamp after every edit with `tools/fix_field1_crc.py`.
- **Field 3** (0x1FFEF8): not solved and not recomputed. A CKTEST bin booting on the bench shows whether
  it is enforced.

## ECU variant warning

The SD bins are built on 5JCZSJ40. 5JCZSJ10 differs in more than ID bytes: for example,
"ETV Limit A | Neutral, Gears 1-2" differs in 559 of 897 cells. On a 10L1 bike, flashing an SD bin also
changes neutral, 1st and 2nd gear throttle limiting.
