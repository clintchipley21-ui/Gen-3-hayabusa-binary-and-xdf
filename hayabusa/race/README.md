# Race software — speed density + rolling anti-lag

Custom build of 5JCZSJ40 (ECM 32990-10L4) for a boosted Gen 3 Hayabusa. Unverified on hardware:
boot a CKTEST bin on a bench ECM first, and keep the stock read for recovery.

## Current files

| File | Use |
|---|---|
| `Busa-SD-v4.1.bin` | The original SD + anti-lag bin. Anti-lag ships **disabled**. |
| `Busa-Race-v1.bin` | Full race bin: SD + anti-lag + air-shift + boost, built from 5JCZSJ40 and edited to an **example working configuration** (boost-by-gear 20→90 %, air-shift at 10,500, anti-lag armed, closed-loop boost off). Still **unverified** — calibrate injectors + sensor and bench the outputs first. See [`notes/race-v1.txt`](notes/race-v1.txt). Rebuild: `python3 ../tools/apply_patches.py ../stock/5JCZSJ40/5JCZSJ40.bin Busa-Race-v1.bin`. |
| `Busa-SD-v6.xdf` | Open this in TunerPro. XDF v6 = the full stock XDF v9.3 (quickshifter decode, top-speed limiter, unit audit, every auto-defined item traced) plus the race definitions: SD fuel maps, ALS / boost spark maps, sensor scaling, and the patch tuning items (anti-lag, air-shift, boost control, MAP-sensor presets) in folder `22 Patches & Air-Shifter`. Values are from the SD-v4.1 bin; items the race software changed are marked. Same numbered workflow folders as the stock XDFs (start in `00 Start Here`; race items are also in `20 Race`). Short descriptions (<= 420 chars) keep TunerPro from crashing; full notes are in `docs/xdf-notes.csv`. Rebuild with `python3 tools/make_race_xdf.py`. |

## Versions

Each version builds on the one before. Full byte-level change lists are in `notes/`.

| Version | Bin | XDF | What changed |
|---|---|---|---|
| SD-v1 | `old/SD-v1.bin` | — | MAP sensor rescaled to a 3-bar part, fuel lookup moved from vacuum to absolute pressure, in-gear fuel maps re-axised 20–300 kPa. |
| SD-v2 | `old/SD-v2.bin` | `old/SD-v2.xdf` (serves SD-v1 and SD-v2) | Speed-density map holds fuel authority at all throttle openings (blend curve and WOT gate disabled); neutral/clutch maps re-axised. |
| SD-v3 | `old/SD-v3.bin` | `old/SD-v3.xdf` | Rest of the ECU back on the stock pressure scale; SD fuel and new boost spark map read the raw IAP ADC; IAP fault threshold raised. |
| SD-v4 | `old/SD-v4.bin` | `old/SD-v4.xdf` (later `old/SD-v5.xdf`, `old/SD-v5-test26.xdf`) | Rolling anti-lag (START button + WOT captures RPM, spark cut + timing retard). Source in `als/`. |
| SD-v4.1 | `Busa-SD-v4.1.bin` | `Busa-SD-v6.xdf` | Anti-lag disabled by default; anti-lag time limit can no longer be reset by re-capturing. |

## Build a race bin from a stock read — one command

`tools/apply_patches.py` turns a stock 5JCZ read into a boosted race bin and re-stamps the field-1 CRC
automatically. The `antilag`, `autoshift` and `boost` code patches touch only free/identical flash, so
they drop onto **any** of the eight reads. The `sd` patch replaces fuelling calibration lifted from
`5JCZSJ40`; that calibration is shared by every read **except `5JCZSJB0`**, and the script checks the
base bytes and aborts safely (writing nothing) on any read whose fuelling differs. Everything is
**unverified on hardware**; the engine features below ship **disabled**.

    python3 ../tools/apply_patches.py stock.bin race.bin                    # sd + antilag + autoshift + boost
    python3 ../tools/apply_patches.py stock.bin out.bin sd                  # pick patches: sd antilag autoshift boost
    python3 ../tools/apply_patches.py stock.bin out.bin sd --sensor gm25bar # speed density on a GM 2.5-bar sensor
    python3 ../tools/apply_patches.py race.bin   /dev/null --check          # report what is already applied

The four patches (applied in a fixed order so their one shared map resolves the same every time):

| Patch | What it adds |
|---|---|
| `sd` | **Speed density on a 3-bar MAP sensor.** Rescales the IAP sensor, repoints the fuel lookups from manifold vacuum to absolute pressure, **disregards the throttle (TPS / alpha-N) fuel path** (the MAP table holds authority everywhere), re-axises all 8 SD fuel maps, and adds the boost spark-retard maps. This is the full SD-v3 change set (23,730 bytes) lifted byte-for-byte out of `old/SD-v3.bin`. Needs injector scaling + a sensor calibration before it runs. |
| `antilag` | The SD-v4.1 rolling anti-lag (code 0xBE000, settings 0xBF000, retard map, three hooks). Enable/tune with the `ALS ...` items. |
| `autoshift` | Auto-upshift (air-shifter): at a per-gear RPM target, pulses the PAIR output → relay → MAC valve → air ram. No spark cut (the factory quickshifter does that). Tune with `Auto-Shift ::`. See [`notes/autoshift.txt`](notes/autoshift.txt). |
| `boost` | **Boost control:** software-PWMs a race-unused output (the repurposed O2-heater driver) to a wastegate/boost-control solenoid, duty scheduled per gear, with optional closed-loop trim from a pressure sensor on a repurposed O2 signal input. Tune with `Boost ::`. See [`notes/boost.txt`](notes/boost.txt). Only applied once `als/boost.bin` has been assembled (`als/build.sh`); if missing it is skipped with a note. |

`sd antilag` (no air-shift/boost) reproduces the shipped `Busa-SD-v4.1.bin` byte-for-byte.

Then open the patched bin in its XDF and enable/tune in the `22 Patches & Air-Shifter` folder. The patches
are applied by the script, not from inside TunerPro: native TunerPro patch elements (XDFPATCH) crashed
TunerPro on open, so they are not embedded in the XDFs.

The air-shifter's PAIR output bit **and** the boost solenoid's O2-heater output bit are unverified: confirm
each on the bench with its XDF `... :: Bench Test Output` switch before trusting it (procedures in
`notes/autoshift.txt` and `notes/boost.txt`).

### MAP-sensor presets (IAP tables)

The `sd` patch scales the IAP tables for a wide-range MAP sensor. Pick the sensor with `--sensor`; the
scaling is just the 16-bit gain/offset at 0x18EF58/5A (the conversion divisor and fault threshold are
sensor-independent). Both are **provisional** — true them with one key-on reading (`raw*a + b` should equal
local barometric) and set the XDF kPa equation on the SD fuel/boost maps to match.

| `--sensor` | Transfer (kPa = a·raw + b) | GAIN | OFFSET |
|---|---|---|---|
| `gm3bar` (default) | a=0.307429, b=−12.6 (~62.9 kPa/V, span ~20–300 kPa) | 0xA12F | 0x6CA6 |
| `gm25bar` | a=0.256598, b=−10.5 (~52.5 kPa/V, span ~20–250 kPa) | 0x8689 | 0x6FE0 |

Formula for any sensor: `GAIN = round(393.14·a·10925/32)`, `OFFSET = round(32768 + 393.14·b)`. The XDF
`IAP Sensor :: Conversion Divisor` item (every XDF) carries both presets and this formula in its description.

## Anti-lag source (`als/`)

- `als.s` — GNU as source (`-mv850e3v5`) for `ALS_TICK`, `ALS_LIMIT` and `ALS_IS_ACTIVE` at 0xBE000.
  Assembled and linked at 0xBE000 it reproduces the SD-v4.1 code bytes exactly. The SD-v4 version had
  `st.h r0, 4[r10]` where SD-v4.1 has two NOPs.
- `als_harness.s` — simulator test harness. It needs `blob_*.bin` extracts of the stock code, which are not
  in this repo.
- `autoshift.s` — GNU as source for the auto-upshift / air-shifter (`AUTOSHIFT_TICK` at 0xBE148).
- `autoshift.bin` — the assembled blob `apply_patches.py` installs.
- `boost.s` — GNU as source for boost control (`BOOST_TICK` at 0xBE280): per-gear software-PWM of the
  repurposed O2-heater output, with optional closed-loop trim. Hardware I/O is isolated to the
  `OUT_ON`/`OUT_OFF` macros and the `PRESS_IN` address (bench-confirmed; see `notes/boost.txt`).
- `boost.bin` / `boost.hook` — the assembled 330-byte blob and its hook word (`0x5DCA2` → `BOOST_TICK`),
  installed by `apply_patches.py`.
- `build.sh` — assembles `als.s`, `autoshift.s` and `boost.s` with an RH850 binutils build and prints the
  hook words. Re-assembling `als.s`/`autoshift.s` reproduces the shipped bytes exactly
  (`als.bin` == SD-v4.1 0xBE000 region, `autoshift.bin` == the committed blob).

## Corrections to the earlier manifests (XDF v9.2 audit)

- **0x1824C6 is a tip-in rate gate, not a WOT gate.** SD-v2/SD-v3 manifests call it the "WOT throttle-path
  gate, 91.4 deg". The code compares it with the throttle opening *rate* (TP now - TP 4 samples ago), so
  stock 33282 means "TP rises 1.41 deg or more within 4 samples". Setting it to 0xFFFF (done since SD-v2)
  still has the intended result - the speed-density map keeps authority - but on fast tip-in, not at WOT.
- RAM `fef02634` / `fef02636` are front / rear wheel speed, `fef02604` is throttle opening rate and
  `fef01562` is the traction-control slip error. The current race XDF (v6) includes these corrections; `old/` keeps the SD-v5 / test26
  XDFs with only the v9.2 corrections applied.
- Anti-lag is unaffected: `als.s` reads `fef0263A`, verified as the averaged front wheel speed.

## After editing a bin

Re-stamp the field-1 CRC: `python3 ../tools/fix_field1_crc.py your.bin`

## Old file names

Files were renamed to keep paths short. `Hayabusa-5JCZSJ40-race-software-SD-vN.bin` is now `old/SD-vN.bin`
(SD-v4.1: `Busa-SD-v4.1.bin`); `Hayabusa-Gen3-5JCZSJ40-5JCZSJ10-race-software-SD[-vN].xdf` is now `old/SD-v2.xdf` /
`old/SD-vN.xdf`; `Hayabusa-Gen3-race-software-SD-v6.xdf` is now `Busa-SD-v6.xdf`; `manifests/SD-vN-manifest.txt`
is now `notes/SD-vN.txt`.
