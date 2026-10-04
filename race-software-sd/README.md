# Race software — speed density + rolling anti-lag

Custom build of 5JCZSJ40 (ECM 32990-10L4) for a boosted Gen 3 Hayabusa. Unverified on hardware:
boot a CKTEST bin on a bench ECM first, and keep the stock read for recovery.

## Current files (`current/`)

| File | Use |
|---|---|
| `Hayabusa-5JCZSJ40-race-software-SD-v4.1.bin` | The bin to flash. Anti-lag ships **disabled**. |
| `Hayabusa-Gen3-5JCZSJ40-5JCZSJ10-race-software-SD-v5-test26.xdf` | Open this in TunerPro. Same definitions as SD-v5 with the header description shortened, because the full text crashes TunerPro. |
| `Hayabusa-Gen3-5JCZSJ40-5JCZSJ10-race-software-SD-v5.xdf` | SD-v5 with the full header description (anti-lag and SD usage notes). Reference only. |

## Versions

Each version builds on the one before. Full byte-level change lists are in `manifests/`.

| Version | Bin | XDF | What changed |
|---|---|---|---|
| SD-v1 | `history/bins/…-SD-v1.bin` | — | MAP sensor rescaled to a 3-bar part, fuel lookup moved from vacuum to absolute pressure, in-gear fuel maps re-axised 20–300 kPa. |
| SD-v2 | `history/bins/…-SD-v2.bin` | `history/xdfs/…-race-software-SD.xdf` | Speed-density map holds fuel authority at all throttle openings (blend curve and WOT gate disabled); neutral/clutch maps re-axised. |
| SD-v3 | `history/bins/…-SD-v3.bin` | `history/xdfs/…-SD-v3.xdf` | Rest of the ECU back on the stock pressure scale; SD fuel and new boost spark map read the raw IAP ADC; IAP fault threshold raised. |
| SD-v4 | `history/bins/…-SD-v4.bin` | `history/xdfs/…-SD-v4.xdf` | Rolling anti-lag (START button + WOT captures RPM, spark cut + timing retard). Source in `als/`. |
| SD-v4.1 | `current/…-SD-v4.1.bin` | `current/…-SD-v5-test26.xdf` | Anti-lag disabled by default; anti-lag time limit can no longer be reset by re-capturing. |

## Anti-lag source (`als/`)

- `als.s` — GNU as source (`-mv850e3v5`) for `ALS_TICK`, `ALS_LIMIT` and `ALS_IS_ACTIVE` at 0xBE000.
  Assembled and linked at 0xBE000 it reproduces the SD-v4.1 code bytes exactly. The SD-v4 version had
  `st.h r0, 4[r10]` where SD-v4.1 has two NOPs.
- `als_harness.s` — simulator test harness. It needs `blob_*.bin` extracts of the stock code, which are not
  in this repo.

## Corrections to the earlier manifests (XDF v9.2 audit)

- **0x1824C6 is a tip-in rate gate, not a WOT gate.** SD-v2/SD-v3 manifests call it the "WOT throttle-path
  gate, 91.4 deg". The code compares it with the throttle opening *rate* (TP now - TP 4 samples ago), so
  stock 33282 means "TP rises 1.41 deg or more within 4 samples". Setting it to 0xFFFF (done since SD-v2)
  still has the intended result - the speed-density map keeps authority - but on fast tip-in, not at WOT.
- RAM `fef02634` / `fef02636` are front / rear wheel speed, `fef02604` is throttle opening rate and
  `fef01562` is the traction-control slip error. The race XDFs in `current/` are corrected
  (`tools/xdf_corrections.py`); the XDFs in `history/` are kept as originally published.
- Anti-lag is unaffected: `als.s` reads `fef0263A`, verified as the averaged front wheel speed.

## After editing a bin

Re-stamp the field-1 CRC: `python3 ../tools/fix_field1_crc.py your.bin`
