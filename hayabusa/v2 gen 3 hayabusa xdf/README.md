# v2 Gen 3 Hayabusa XDF (decompile-traced, reproducible, for CalStudio)

A second-pass Hayabusa Gen 3 XDF built the same way the sibling GSX-R XDFs are: a full Ghidra
decompile drives a single, reproducible generator that ties every table, scalar, flag and DTC
back to the code that reads it. Built for **CalStudio** (no TunerPro length/category limits), so
every item keeps its full inline notes.

> **Everything here is unverified on hardware.** Bench an ECM first and keep a stock read for
> recovery. v2 does not change any editable definition vs the current XDF (see below) - it is a
> better-documented, reproducible build of the same calibration.

## The short version

- The current Hayabusa XDF (`../stock/master/master-v9.xdf`) is already a complete,
  decompile-driven definition - 757 tables, 2,768 constants, 235 flags, every one of the 749
  on-bin map descriptors verified, every code-read scalar role-traced, 0 generic titles. It is
  the mature parent the GSX-R XDFs were ported from, not a rough draft.
- So v2's job is not to *find* new editable items (the independent rebuild reaches the same 3,760
  items, which confirms the editable surface is fully enumerated). v2's job is to make that
  definition **reproducible**, raise and **standardize the map-input tracing**, push the
  decompile a little **deeper** on the residual unknowns, and lay it out cleanly.
- **A machine diff proves v2 changes 0 calibration definitions** (every address, size, stride,
  axis, scaling equation and flag mask is byte-identical to v9). v2 only improves documentation.

Full numbers and discussion: [`docs/COMPARISON.md`](docs/COMPARISON.md).

## What's here

```
busa-v2-master.xdf     the v2 definition, full text, valued for 5JCZSJ10 (reference master)
<software>-v2.xdf      one full-text v2 per stock read (5JCZSJ00/10/20/30/40/A0/B0, NC0),
                       each carrying that read's own stock values + DIFFERS-from-5JCZSJ10 tags
                       (any one opens any stock read; only the stock-value text is read-specific)
<software>-function-index.csv  per-read copy of the function index (identical across reads)
tools/
  make_busa_v2_xdf.py      the generator: enhance master-v9 from the decompile, emit master + reads
  busa_v2_common.py        decompile joins (RAM meanings, traced inputs, DTC names, legends, units)
  make_function_index.py   build the function-index spreadsheet(s) for CalStudio
docs/
  COMPARISON.md            v2 vs master-v9: the machine diff, coverage, and the discussion
  function-index.csv       every referenced function: address, handle, name, subsystem, maps/signals
  manual-verification.md   service-manual sensor-scaling + DTC verification (manual kept in Dropbox)
  manual-dtc-names.csv     68 official SAE DTC names from the Suzuki Gen3 service manual
  busa-v2-ram-names.csv    v2 deep-trace: axis/compared RAM variables resolved from all_functions.c
```

### Value legends, units and DTC names (this round)

- **Every flag (235)** carries an explicit legend - `0x80 = ON / 0x00 = OFF`, or `bit0 = MIL
  enable` for the DTC lamp bytes - and **every constant (2,768)** carries a value legend.
- Raw threshold scalars are shown in meaningful units (RPM, deg, kPa, km/h, V, degC) wherever the
  code proves the unit by comparing the scalar against a known sensor variable; the rest stay raw
  with a legend saying so (no fabricated units).
- **120 DTC enable flags** carry the service manual's official SAE name. Sensor scalings were
  checked against the Suzuki Gen3 service manual (idle 1050-1250 rpm, NTC ECT/IAT tables, 0-5 V
  TP/APS) - all consistent, none changed. See `docs/manual-verification.md`.
- The sibling GSX-R M7 XDFs got the same legend pass, a function index, and a fix to their
  per-cylinder fuel-map labels - see `../../gsxr-1000/docs/cylinder-fuel-maps.md`.

### Patches, ETV maps, category name (this round)

- **Rolling anti-lag + auto-upshift (air-shifter) settings** are now in every per-read v2 XDF,
  under the folder **"22 Patches & Air-Shifter (apply to a stock bin)"** (10 Auto-Shift items +
  9 ALS items), the same set the stock per-read XDFs carry. These are the *tuning items*; the
  patch *code* is written to the bin by `../tools/apply_patches.py` (which also re-stamps the
  field-1 CRC). Both ship DISABLED and are UNVERIFIED - bench first. The full-text
  `busa-v2-master.xdf` stays patch-free (reference), matching the stock master.
- **ETV limiting maps - audited complete.** v2 defines the whole throttle-limiting stack: base
  ETV Limit A (per gear), ETV-PWR 1/2/3 targets (Neutral + Gears 1-6), TC / LF (anti-lift) /
  Launch per-gear throttle limits, Engine-Brake throttle opening, Cruise throttle, and the ~110
  ETV Monitor Level-2 safety-limit maps. With 0 generic titles and all 749 descriptors defined,
  no ETV-limit descriptor is missing or unlabelled.
- The root category tab **"xdf moto bin files"** is renamed to **"xdf bin files"**.

## What v2 adds over the current XDF

1. **Standardized map-input tracing on every table.** Each table that the decompile resolves
   carries one machine-parseable line:
   `TRACED INPUTS (v2 decompile): X = <meaning> (RAM 0x..); Y = <meaning> (RAM 0x..). Read by FUN_..`
   Coverage: **636 of the 749 descriptor-backed tables** (the other 113 are data-only or read by
   inlined/computed indexing - no single sensor axis, so no line is fabricated). The X-axis
   *meaning* resolves on ~632/747, up from 397 in the raw decompile, by joining each axis RAM
   variable to its verified meaning in `../docs/ram-variables.csv` + the decompile's `ram_inputs.csv`.

2. **Reproducibility.** One documented generator rebuilds the whole definition from the bin, the
   shipped decompile (`../re/decompiled.zip`) and master-v9 - so it can be regenerated, audited and
   extended from data files instead of by hand-editing 4.4 MB of XML. Same model as
   `../../gsxr-1000/tools/make_gsxr_xdf.py`.

3. **A bounded, honest deep-trace** of the axis RAM variables master-v9 left unnamed
   (`0xFEF01567`, `0xFEF02644`, `0xFEF0135C`, `0xFEF0268C`, `0xFEF0267A`), traced from their writer
   functions in `all_functions.c`. They turn out to feed ETV-aux and currently-flat/unused curves
   and are centered/rate-limited intermediate signals, so they are role-labelled with honest
   confidence, never guessed into fake functional names. See `docs/busa-v2-ram-names.csv`.

4. **A clean category set** (the legacy empty "Unidentified - Cluster … (empty)" folder-name
   suffixes are scrubbed).

## Confidence

The per-item confidence (HIGH / MEDIUM / LOW) is carried straight from the code trace, unchanged
from v9: **823 HIGH, 1,074 MEDIUM, 375 LOW** across the 2,272 auto-defined scalars. HIGH = the
role was read directly from a comparison / axis / switch; MEDIUM = role known, other operand not
identified; LOW = referenced but the use did not resolve (indirect/structure access). The v2
TRACED INPUTS lines carry a `[confidence]` tag where the axis meaning is not high-confidence.
**Log before changing anything, and change one thing at a time.**

## Regenerate

```
# from the repo root
python3 "hayabusa/v2 gen 3 hayabusa xdf/tools/make_busa_v2_xdf.py" --all     # master + all 8 reads
python3 "hayabusa/v2 gen 3 hayabusa xdf/tools/make_busa_v2_xdf.py" 5JCZSJ40 32990-10L4   # one read
```

Add resolved RAM variables to `docs/busa-v2-ram-names.csv` or code-proven item upgrades to
`docs/busa-v2-trace.csv` (columns: `address,new_title,confidence,note`) and re-run - no code change
needed.

## Checksums

Same as the rest of the repo: re-stamp the **field-1** CRC-16/CCITT-FALSE
(`0x10000-0x1FFAFB`, big-endian at `0x1FFAFE`) with `../tools/fix_field1_crc.py` after editing.
Field 3 (`0x1FFEF8`) is not solved and not recomputed.
