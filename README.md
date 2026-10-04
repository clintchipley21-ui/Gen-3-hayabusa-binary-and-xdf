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
| Edit any stock read | [`stock/xdf/per-read/Hayabusa-Gen3-<software>-stock-v9.xdf`](stock/xdf/per-read/), matching the software number in the read's filename |
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
  reads/                   unmodified 2 MB reads, named <ECM part>-<software>.bin
  reads/other-software/    reads from other software families (see below)
  xdf/                     stock fuel-strategy XDF v9 (master, written for 5JCZSJ10) and its manifest
  xdf/per-read/            one XDF per stock read, generated from the master by tools/make_stock_xdfs.py
  xdf/history/             stock XDFs v2 to v8 (there is no v6)
reverse-engineering/       Ghidra project and decompiled C for 5JCZSJ40
docs/                      RAM variable list, DTC table, decoded index of the SD-v5 XDF
tools/                     fix_field1_crc.py, make_stock_xdfs.py
```

## Stock reads

Every read in `stock/reads/` has byte-identical code (0x10000–0x14FFFF) and a valid field-1 CRC.
Every byte that differs between the reads lies inside an item the stock XDF defines (apart from an ID
string and one variant word, which the per-read XDFs add), so map descriptors, addresses and sizes are
the same in all of them. Each read has its own XDF in `stock/xdf/per-read/` with that read's stock values;
items whose data differs from 5JCZSJ10 say so in their description. Calibration bytes differ from 5JCZSJ40
by the amounts below.

| File | ECM | Software | Calibration bytes different from 5JCZSJ40 |
|---|---|---|---|
| `32990-10L0x-5JCZSJ00.bin` | 32990-10L0 | 5JCZSJ00 | 22 |
| `32990-10L1x-5JCZSJ10.bin` | 32990-10L1 | 5JCZSJ10 | 1,032 (stock v9 XDF verified on this read) |
| `32990-10L2x-5JCZSJ20.bin` | 32990-10L2 | 5JCZSJ20 | 5 |
| `32990-10L3x-5JCZSJ30.bin` | 32990-10L3 | 5JCZSJ30 | 1,029 |
| `32990-10L4x-5JCZSJ40.bin` | 32990-10L4 | 5JCZSJ40 | — (base for every SD bin) |
| `32920-10LAx-5JCZSJA0.bin` | 32920-10LA | 5JCZSJA0 | 18 |
| `32920-10LBx-5JCZSJB0.bin` | 32920-10LB | 5JCZSJB0 | 123,307 |
| `32920-10LCx-5JCZSNC0.bin` | 32920-10LC | 5JCZSNC0 | 252 |

`stock/reads/other-software/` holds files the XDFs here do **not** fit:

- `Hayabusa-Gen3-stock-5JCXSJ10.bin` — software 5JCXSJ10, from the original DanCycles HayabusaGen3 project
  (see [NOTICE.md](NOTICE.md)). Roughly 700 KB of code differs from 5JCZSJ10, and the field-1 CRC method
  below does not match it.
- `32990-10L4-5JCUSJ40.ori` — software 5JCUSJ40 in a 2,031,679-byte container, not a plain 2 MB read.

## Checksums

- **Field 1**: CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF) over 0x10000–0x1FFAFB, stored big-endian at
  0x1FFAFE. Re-stamp after every edit with `tools/fix_field1_crc.py`.
- **Field 3** (0x1FFEF8): not solved and not recomputed. A CKTEST bin booting on the bench shows whether
  it is enforced.

## ECU variant warning

The SD bins are built on 5JCZSJ40. 5JCZSJ10 differs in more than ID bytes: for example,
"ETV Limit A | Neutral, Gears 1-2" differs in 559 of 897 cells. On a 10L1 bike, flashing an SD bin also
changes neutral, 1st and 2nd gear throttle limiting.
