# 5JCUSJ40 full-flash dump — what the complete read reveals

Two files were supplied for the Gen-3 Hayabusa:

| Upload | What it is | Added to repo as |
|---|---|---|
| `...32990-10L4.mot` | Motorola S-record (Renesas Flash Programmer "RFP3" output), decodes to a **complete 2 MB plaintext** flash image, cal ID **`5JCUSJ40`** | `stock/other/5JCUSJ40-full.mot` (source) + `stock/other/5JCUSJ40-full.bin` (decoded) |
| `...32990-10L0..._5JE0SJ00_MF1.bin` | Raw `0x1F0000` read (front 64 KB omitted), plaintext, cal ID **`5JE0SJ00`** — a market variant not previously in the repo | `stock/other/5JE0SJ00.bin` |

Decode is reproducible: `tools/decode_srec.py 5JCUSJ40-full.mot out.bin` →
sha256 `ac23ced9887ac9c184b2deb3cabd0c96853a7fcc2a5da14560f4c8a3d8457dd0`.

## Why this dump matters: our old copy was half-encrypted and truncated

The repo already had `stock/other/5JCUSJ40.ori` for the **same calibration ID**, but it
was only usable for tuning, never for code analysis:

- **The entire lower ~1.2 MB (all program code) was encrypted.** In the `.ori`,
  offsets `0x000000–0x12FFFF` have **entropy 8.00** (indistinguishable from random) —
  a single encrypted container. The calibration half (`0x130000+`) was plaintext,
  which is why its maps and ID strings read fine and matched the stock XDFs.
- **The first 64 KB was missing entirely** (`.ori` is `0x1F003F`, i.e. flash minus
  the front block).

The new `.mot` is the **first fully-decrypted, complete** read of `5JCUSJ40`.
Over the `.ori`'s plaintext calibration region the two agree to **0.006 %** (35 bytes),
confirming same calibration — but the `.mot` additionally exposes everything the `.ori`
hid. See `fulldump-vs-ori.csv`.

### Newly-available regions (vs the `.ori` we had)

| Region | Size | In the old `.ori` | In the full dump |
|---|---|---|---|
| `0x000000–0x00FFFF` | 64 KB | **absent (truncated)** | boot block (vectors + Primary Boot Loader) |
| `0x010000–0x0BDFFF` | ~696 KB | **encrypted (entropy 8.0)** | plaintext RH850 program code |
| `0x140000–0x1BDFFF` | ~720 KB | plaintext (already had) | identical calibration/data |

Net new readable material we never had for this firmware: **~760 KB of program code
plus the 64 KB boot block.**

## The boot block (`0x0–0xFFFF`) — brand new, in no previous repo file

All committed `5JCZ*` stock reads blank `0x0–0xFFFF` to `0xFF`, and the `.ori`
truncates it. The full dump is the only file here that contains it. It identifies the
silicon and carries the reprogramming firmware (see `fulldump-bootblock.csv`):

- `0x0020` **`PBL_RH_TMC_010B_S Ver1.40r2`**, `0x0040` **`mPBL_DUMMY Ver1.10r1`** —
  the Renesas **Primary Boot Loader** (on-chip flash-reprogramming firmware).
- `0x0010` signature `AC 35 53 CA / A5 5A 5A A5 …` — Renesas ID-code / flash-protection area.
- `0xC5C8` device-ID table: **`R7F701201 / 202 / 204 / 205 / 206`, `R7F701Z04–Z07`**
  → the MCU is a **Renesas RH850/F1L**. This pins the exact Ghidra processor
  (`RH850:LE:32`), which was previously only inferred.
- `0x02800–0x0DC20` (~46 KB) — the Primary Boot Loader program code itself.
- `0x0FFE0` **`ECM-010L0-0`** part string.

## Relationship to the existing (5JCZ) decompilation

The repo's `re/decompiled.zip` (8,014 functions) was produced on the **5JCZ line**
(`v9-notes`: "decompiled 5JCZSJ40", "verification done on 5JCZSJ10"). The uploads are a
**different firmware line** (`5JCU` / `5JE0`). Classifying every existing decompiled
function by whether its bytes are the same at the same address in the new dump
(`fulldump-func-classification.csv`):

| Class | Functions |
|---|---|
| identical (decompile reusable as-is) | 174 |
| near-identical, <5 % bytes differ | 81 |
| **substantially different (own pass needed)** | **7,711** |
| other (erased / boot-only) | 46 |

Only **~255 functions (≈3 %)** — the shared bootstrap/early region around
`0x00E000–0x018000` — carry over from the 5JCZ decompile. The two lines share a common
boot/startup base but **diverge across essentially the whole application layer**
(`0x01C000–0x0BDFFF`, ~663 KB, see `fulldump-region-map.csv`). The calibration region is
same-*structure*, different-*values* (identical axis/descriptor blocks, different map
data) — expected for a different market tune.

**Conclusion:** the full dump is not a better copy of code we already understood — it is
a distinct, previously-unreadable firmware image. The existing C decompilation does **not**
map onto it beyond the small shared bootstrap, so the 5JCU/5JE0 application needs its own
decompilation pass.

## Reproducing the decompilation

Full C decompilation requires Ghidra (its bundled RH850 module), the same tool used for
the existing `re/` artifacts. It could not be run in the cloud session that produced this
analysis (Ghidra's download host and local toolchain builds are both blocked there). To
generate it where Ghidra is available:

```
analyzeHeadless <proj> busa5jcu \
  -import hayabusa/stock/other/5JCUSJ40-full.bin \
  -loader BinaryLoader -loader-baseAddr 0x0 -processor "RH850:LE:32:default" \
  -postScript hayabusa/tools/ghidra_export_fulldump.py <out_dir> -deleteProject
```

This writes `all_functions_5jcu.c` + `functions_5jcu.csv`, matching the existing
`decompiled.zip` layout. Flash maps at `0x0`; RAM/peripherals at `0xFE000000–0xFFFFFFFF`
(the `ram:fffxxxxx` addresses in the existing decompile).

## Data files

- `fulldump-region-map.csv` — segmentation of the 2 MB image (code / data / erased).
- `fulldump-vs-ori.csv` — region-by-region: what `5JCUSJ40.ori` had vs the full dump.
- `fulldump-bootblock.csv` — boot-block sub-regions and embedded strings.
- `fulldump-func-classification.csv` — existing-decompile functions vs the new dump.
- `fulldump-shared-functions.csv` — the ~255 functions that carry over unchanged.
