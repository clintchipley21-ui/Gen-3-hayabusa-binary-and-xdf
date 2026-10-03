# Gen 3 Hayabusa — binaries and XDFs

Suzuki Hayabusa Gen 3 (RH850/E1L), full 2 MB reads of 5JCZSJ40 (ECM 32990-10L4) and 5JCZSJ10 (32990-10L1).
Everything here is **unverified on hardware**. Bench an ECM first and keep the stock read for recovery.

## Layout

| Path | What it is |
|---|---|
| `race-software-SD/Hayabusa-5JCZSJ40-race-software-SD-v4.1.bin` | Current race bin: speed-density fuel on a 3-bar IAP sensor, boost spark retard, rolling anti-lag (ALS **disabled** by default). Built on 5JCZSJ40. |
| `race-software-SD/Hayabusa-Gen3-5JCZSJ40-5JCZSJ10-race-software-SD-v5.xdf` | TunerPro definition for the SD bins (SD-v4 and SD-v4.1 share the same layout). |
| `race-software-SD/manifests/` | Per-version change lists, SD-v1 through SD-v4.1. Each lists every changed byte and the bench sequence. |
| `race-software-SD/src/als.s`, `als_harness.s` | Anti-lag source (GNU as, `-mv850e3v5`) and its simulator test harness. |
| `stock-xdf/Hayabusa-Gen3-5JCZSJ10-stock-v9.xdf` | Stock fuel-strategy XDF for an unmodified 5JCZSJ10 or 5JCZSJ40 read. |
| `stock-xdf/v9-manifest.txt` | What the v9 stock XDF covers and how the stock fuel strategy works. |
| `tools/fix_field1_crc.py` | Re-stamps the field-1 CRC after editing a bin. |
| `docs/` | RAM variable list, DTC table, and the decoded index of the v5 XDF. |

## Checksums

- **Field 1**: CRC-16/CCITT-FALSE over 0x10000–0x1FFAFB, stored big-endian at 0x1FFAFE.
  Re-stamp after every edit: `python3 tools/fix_field1_crc.py tuned.bin`
- **Field 3** (0x1FFEF8): not solved and not recomputed. A CKTEST bin booting on the bench is what shows whether it is enforced.

## ECU variant

The SD bins are built on 5JCZSJ40. 5JCZSJ10 differs in more than ID bytes. For example,
"ETV Limit A | Neutral, Gears 1-2" differs in 559 of 897 cells. On a 10L1 bike, an SD bin also
changes neutral, 1st and 2nd gear throttle limiting. See the SD-v4.1 manifest.
