# Race software — speed density + rolling anti-lag

Custom build of 5JCZSJ40 (ECM 32990-10L4) for a boosted Gen 3 Hayabusa. Unverified on hardware:
boot a CKTEST bin on a bench ECM first, and keep the stock read for recovery.

## Current files

| File | Use |
|---|---|
| `Busa-SD-v4.1.bin` | The bin to flash. Anti-lag ships **disabled**. |
| `Busa-SD-v6.xdf` | Open this in TunerPro. XDF v6 = the full stock XDF v9.3 (quickshifter decode, top-speed limiter, unit audit, every auto-defined item traced) plus the race definitions: SD fuel maps, ALS / boost spark maps, sensor scaling, ALS settings. Values are from the SD-v4.1 bin; items the race software changed are marked. Same numbered workflow folders as the stock XDFs (start in `00 Start Here`; race items are also in `20 Race`). Short descriptions (<= 420 chars) keep TunerPro from crashing; full notes are in `docs/xdf-notes.csv`. Rebuild with `python3 tools/make_race_xdf.py`. |

## Versions

Each version builds on the one before. Full byte-level change lists are in `notes/`.

| Version | Bin | XDF | What changed |
|---|---|---|---|
| SD-v1 | `old/SD-v1.bin` | — | MAP sensor rescaled to a 3-bar part, fuel lookup moved from vacuum to absolute pressure, in-gear fuel maps re-axised 20–300 kPa. |
| SD-v2 | `old/SD-v2.bin` | `old/SD-v2.xdf` (serves SD-v1 and SD-v2) | Speed-density map holds fuel authority at all throttle openings (blend curve and WOT gate disabled); neutral/clutch maps re-axised. |
| SD-v3 | `old/SD-v3.bin` | `old/SD-v3.xdf` | Rest of the ECU back on the stock pressure scale; SD fuel and new boost spark map read the raw IAP ADC; IAP fault threshold raised. |
| SD-v4 | `old/SD-v4.bin` | `old/SD-v4.xdf` (later `old/SD-v5.xdf`, `old/SD-v5-test26.xdf`) | Rolling anti-lag (START button + WOT captures RPM, spark cut + timing retard). Source in `als/`. |
| SD-v4.1 | `Busa-SD-v4.1.bin` | `Busa-SD-v6.xdf` | Anti-lag disabled by default; anti-lag time limit can no longer be reset by re-capturing. |

## Code patches — add anti-lag and/or the air-shifter to a stock bin

Two code patches can be dropped onto **any** stock 5JCZ read (every byte region they touch is identical
across the eight reads). Both ship **disabled** and both are **unverified on hardware**.

| Patch | What it adds |
|---|---|
| Rolling anti-lag | The SD-v4.1 anti-lag (code 0xBE000, settings 0xBF000, retard map, three hooks). Enable/tune with the ALS items in the race XDF. |
| Auto-upshift (air-shifter) | At a per-gear RPM target, pulses the PAIR-valve output to drive a relay → MAC valve → air ram. No spark cut (the factory quickshifter does that). Tune with the `Auto-Shift ::` items. See [`notes/autoshift.txt`](notes/autoshift.txt). |

Two ways to apply them:

- **Script (guaranteed, re-stamps the CRC):**
  `python3 ../tools/apply_patches.py stock.bin out.bin` (both), or add `antilag` / `autoshift` for one.
- **In TunerPro:** open a stock read with its XDF, Patch Manager → "Install Rolling Anti-Lag" /
  "Install Auto-Upshift", then **re-stamp the field-1 CRC** (`tools/fix_field1_crc.py`) or the ECU may
  reject the bin. The native-patch XML is best-effort — open one XDF first to confirm it loads, and fall
  back to the script if not.

The air-shifter's PAIR output bit is unverified: confirm it on the bench with the XDF
"Auto-Shift :: Bench Test Output" switch before trusting it (procedure in `notes/autoshift.txt`).

## Anti-lag source (`als/`)

- `als.s` — GNU as source (`-mv850e3v5`) for `ALS_TICK`, `ALS_LIMIT` and `ALS_IS_ACTIVE` at 0xBE000.
  Assembled and linked at 0xBE000 it reproduces the SD-v4.1 code bytes exactly. The SD-v4 version had
  `st.h r0, 4[r10]` where SD-v4.1 has two NOPs.
- `als_harness.s` — simulator test harness. It needs `blob_*.bin` extracts of the stock code, which are not
  in this repo.
- `autoshift.s` — GNU as source for the auto-upshift / air-shifter (`AUTOSHIFT_TICK` at 0xBE148).
- `autoshift.bin` — the assembled blob `apply_patches.py` installs.
- `build.sh` — assembles `als.s` and `autoshift.s` with an RH850 binutils build and prints the hook words.
  It re-checks that `als.s` reproduces the SD-v4.1 bytes exactly.

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
