# Gen 3 Hayabusa — binaries and XDFs

Suzuki Hayabusa Gen 3 (2022+, Renesas RH850/E1L). TunerPro XDFs, stock 2 MB reads, and a custom
"race software" build that adds speed-density fuelling on a 3-bar MAP sensor, boost spark retard and
rolling anti-lag.

> **Everything here is unverified on hardware.** Bench an ECM first and keep a stock read for recovery.

## Where to start

| I want to… | Use |
|---|---|
| Flash the current race build | [`race-software-sd/current/Hayabusa-5JCZSJ40-race-software-SD-v4.1.bin`](race-software-sd/current/) |
| Edit the race build in TunerPro | [`race-software-sd/current/…-race-software-SD-v5-test26.xdf`](race-software-sd/current/) |
| Edit a stock read | Open the folder for your read under [`stock/`](stock/): it holds the `.bin` and its matching `.xdf` |
| Fix the checksum after editing | `python3 tools/fix_field1_crc.py tuned.bin` |

## Layout

```
race-software-sd/          custom speed-density + anti-lag build (see its README)
  current/                 SD-v4.1 bin and the SD-v5 XDFs
  manifests/               change list for every SD version, SD-v1 to SD-v4.1
  als/                     anti-lag assembly source and simulator harness
  history/bins/            SD-v1 to SD-v4 bins
  history/xdfs/            the XDFs that went with SD-v1/v2, v3 and v4
stock/
  <ECM>-<software>/        one folder per stock read: <name>.bin and the matching <name>.xdf
  other-software/          reads from other software families (see below)
  xdf-master/              stock XDF v9 (full-length master the per-read XDFs are built from) and its manifest
  xdf-master/history/      stock XDFs v2 to v8 (there is no v6)
reverse-engineering/       Ghidra project and decompiled C for 5JCZSJ40
docs/                      RAM variable list, DTC table, decoded index of the SD-v5 XDF
tools/                     fix_field1_crc.py, make_stock_xdfs.py, xdf_corrections.py
```

## Stock reads

Each folder in `stock/` holds one unmodified 2 MB read and the XDF built for it. All eight reads have
byte-identical code (0x10000–0x14FFFF) and a valid field-1 CRC. Every byte that differs between them lies
inside an item the XDF defines (apart from an ID string and one variant word, which the XDFs add), so map
descriptors, addresses and sizes are the same in all of them.

Each XDF has 758 tables, 2,801 constants and 163 flags. The VALUES / STOCK line in every description is that
read's own value, and items whose data differs from 5JCZSJ10 are marked "DIFFERS FROM 5JCZSJ10".

**TunerPro limits.** The SD-v5 race XDF crashed TunerPro on open because of its long, multi-line header; the
same file with a 490-character header (`test26`) opens, with item descriptions up to 1,372 characters. The
per-read XDFs stay inside that: single-line headers of about 355 characters and every item description at
most 1,300 characters. 32 long descriptions are shortened (least important paragraphs first; values, axes and
addresses are always kept) and say so. The full text is in `stock/xdf-master/`, whose 1,611-character header
and longer descriptions may be too long for TunerPro, so treat it as reference. Regenerate the per-read XDFs
with `python3 tools/make_stock_xdfs.py` after changing the master.

Calibration bytes differ from 5JCZSJ40 by the amounts below.

| Folder | ECM | Software | Calibration bytes different from 5JCZSJ40 |
|---|---|---|---|
| [`32990-10L0x-5JCZSJ00/`](stock/32990-10L0x-5JCZSJ00/) | 32990-10L0 | 5JCZSJ00 | 22 |
| [`32990-10L1x-5JCZSJ10/`](stock/32990-10L1x-5JCZSJ10/) | 32990-10L1 | 5JCZSJ10 | 1,032 (stock v9 XDF verified on this read) |
| [`32990-10L2x-5JCZSJ20/`](stock/32990-10L2x-5JCZSJ20/) | 32990-10L2 | 5JCZSJ20 | 5 |
| [`32990-10L3x-5JCZSJ30/`](stock/32990-10L3x-5JCZSJ30/) | 32990-10L3 | 5JCZSJ30 | 1,029 |
| [`32990-10L4x-5JCZSJ40/`](stock/32990-10L4x-5JCZSJ40/) | 32990-10L4 | 5JCZSJ40 | — (base for every SD bin) |
| [`32920-10LAx-5JCZSJA0/`](stock/32920-10LAx-5JCZSJA0/) | 32920-10LA | 5JCZSJA0 | 18 |
| [`32920-10LBx-5JCZSJB0/`](stock/32920-10LBx-5JCZSJB0/) | 32920-10LB | 5JCZSJB0 | 123,307 |
| [`32920-10LCx-5JCZSNC0/`](stock/32920-10LCx-5JCZSNC0/) | 32920-10LC | 5JCZSNC0 | 252 |

`stock/other-software/` holds files the XDFs here do **not** fit:

- `Hayabusa-Gen3-stock-5JCXSJ10.bin` — software 5JCXSJ10, from the original DanCycles HayabusaGen3 project
  (see [NOTICE.md](NOTICE.md)). Roughly 700 KB of code differs from 5JCZSJ10, and the field-1 CRC method
  below does not match it.
- `32990-10L4-5JCUSJ40.ori` — software 5JCUSJ40 in a 2,031,679-byte container, not a plain 2 MB read.

## Race-relevant settings (stock XDFs, no code patch)

| Setting | Where in the XDF | Stock |
|---|---|---|
| Top-speed limiter (~299 km/h) | `Per-Gear Limiter \| 6th` — a 6th-gear RPM limit, enable 0x15444B | 10,450 soft / 10,550 rpm hard |
| Per-gear rev limits 3rd–5th | `Per-Gear Limiter \| 3rd/4th/5th` | parked at 25,000 rpm (off) |
| Quickshifter cut strategy | `Quickshifter :: Shift Actions` (checkboxes: spark cut, retard, fuel cut + throttle, fuel factor per phase, on- and off-throttle) | see each read's XDF |
| Launch control RPM | `Launch Control \| Level 1-3` and `Launch Control - Throttle Limit` | Level 1 hard cut 3,700 rpm |

## XDF accuracy (v9.2 audit)

Every RAM variable the XDFs use for units was re-checked against the code that writes it, every constant
against the code that compares it, and every table against the ECU's own map descriptors. Five variables
had been mislabelled (two wheel speeds shown as throttle position, throttle rate shown as throttle position,
traction-control slip error shown as grip %, a wheel-derived RPM shown as engine RPM), which put wrong
units on about 120 items. All are fixed in the stock and current race XDFs; details and the method are in
`stock/xdf-master/v9-manifest.txt` and `tools/xdf_corrections.py`. Notably **0x1824C6 is a tip-in rate
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
