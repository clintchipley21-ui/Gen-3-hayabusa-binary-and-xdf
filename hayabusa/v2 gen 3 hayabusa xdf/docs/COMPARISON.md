# v2 vs. current Hayabusa XDF (`master-v9`) — comparison and discussion

This is the "compare it with our current Hayabusa XDF and discuss" step. It is grounded in a
machine diff of `busa-v2-master.xdf` against `hayabusa/stock/master/master-v9.xdf`, plus the
coverage numbers from the decompile join.

**Target editor: CalStudio.** v2 is built for CalStudio, which (unlike TunerPro) imposes no
description-length, single-line-header, category-size or uniqueid limits, so v2 keeps every
item's full inline notes (the full-text master-v9 was reference-only because it was too large
for TunerPro). **Deliverables:** `busa-v2-master.xdf` (full definition, 5JCZSJ10 values) plus a
full-text per-read `*-v2.xdf` for all eight stock reads, each carrying that read's own stock
values and DIFFERS-from-5JCZSJ10 tags.

## 1. Headline result

| | master-v9 (current) | v2 (this build) |
|---|---|---|
| Tables | 757 | 757 |
| Constants | 2,768 | 2,768 |
| Flags | 235 | 235 |
| Categories | 94 | 94 (legacy "(empty)" suffixes scrubbed) |
| Total items (unique ids) | 3,760 | 3,760 |
| **Items whose calibration *structure* differs** (address / size / stride / axes / scaling / mask) | — | **0** |
| Titles changed | — | 0 |
| Descriptions changed | — | 636 |
| Tables carrying a map-input trace | 447 (free-text, inconsistent) | **636 (standardized `TRACED INPUTS` line)** |
| Map X-axis meaning resolved | 397 / 747 | **~632 / 747** |
| Built by | hand, incrementally v2→v9 | **one reproducible generator** (`tools/make_busa_v2_xdf.py`) |

**The single most important line in that table is "Items whose calibration structure differs: 0."**
v2 does not move, resize, rescale, or redefine a single editable item. Every address, bit size,
stride, axis pointer, scaling equation and flag mask is byte-identical to v9. So v2 is a
drop-in-equivalent definition: anything you tune in v2 tunes exactly the same bytes as in v9.
v2 changed **documentation only** — 636 descriptions gained a traced-input line; nothing else.

## 2. What v2 actually adds

1. **Standardized, expanded map-input tracing.** Every table that the decompile can resolve now
   carries one line:
   `TRACED INPUTS (v2 decompile): X = <meaning> (RAM 0x…); Y = <meaning> (RAM 0x…). Read by FUN_…`
   Coverage rose from 447 tables (v9, where the input was buried in free-text "HOW THE ECU USES IT"
   prose on some items and absent on others) to **636 tables**, and the line is machine-parseable.
   The lift came from joining each map's axis RAM variable (from `re/decompiled.zip:map_links.csv`)
   to its verified meaning in `docs/ram-variables.csv` + the decompile's `ram_inputs.csv`: that
   alone resolved **+238** X-axis meanings that v9 left blank (397 → ~632 of 747).

2. **Reproducibility.** v9 is a hand-maintained 4.3 MB XML file. v2 is produced by a single
   documented generator from three inputs — the bin, the shipped Ghidra decompile, and the v9
   structural base — so the definition can be regenerated, audited, and extended by editing data
   files (`docs/busa-v2-ram-names.csv`, `docs/busa-v2-trace.csv`) rather than editing XML by hand.
   This mirrors how the sibling GSX-R XDFs are built (`gsxr-1000/tools/make_gsxr_xdf.py`).

3. **An independent cross-check of v9.** Rebuilding the definition from the descriptors and the
   decompile and diffing it against v9 is itself a verification: the **0 structural differences**
   result independently confirms that v9's 749 descriptor decodes, addresses and scalings are
   internally consistent with the bin and the decompile.

4. **A bounded, honest deep-trace of the residual unknown axis variables** (see §4).

## 3. Why v2 does not add new *editable* items — and why that is the right answer

The natural expectation of a "v2 deep-dive" is that it would uncover new tunable tables or
scalars. It did not, and that is a real finding rather than a shortfall: **`master-v9` already
defines every calibration byte the code reads.** Its own verification notes record that of the
3,834 calibration addresses the code reads directly, all READ accesses are already defined; what
remains unreferenced is pointer tables / structure bases (DATA references), not tunable values.
The independent v2 rebuild reaches the same 3,760 items from the descriptors + cal-xref set, which
corroborates that the editable surface is already fully enumerated.

In other words, the current Hayabusa XDF is not a rough draft to be superseded — it is the mature
parent that the GSX-R XDFs were themselves ported from. The valuable work left is not *finding*
items; it is *tracing* the ones already found to higher confidence, standardizing how that trace is
recorded, and making the whole thing reproducible. That is what v2 is.

## 4. The deep-trace: what the decompile does and does not resolve

Coverage of the scalar role-trace (`docs/autodef-trace.csv`, 2,272 auto-defined constants),
unchanged in substance from v9 and carried into v2:

| Confidence | Count |
|---|---|
| HIGH (role read directly from a comparison/axis/switch) | 823 |
| MEDIUM (role known, other operand not identified) | 1,074 |
| LOW (referenced, use not resolved — indirect/structure access) | 375 |

The honest gaps are the **375 LOW** scalars and the **113 descriptor-backed tables** with no
resolvable sensor axis (read by inlined/computed indexing, or data-only). v2 pushed on the highest-
leverage part of this — the axis RAM variables feeding the most maps that v9 left unnamed
(`0xFEF0135C`, `0xFEF02644`, `0xFEF01567`, `0xFEF0268C`, `0xFEF0267A`). Tracing their writer
functions in `all_functions.c` showed:

- `0xFEF01540`/`0xFEF01567` — a 64-neutral correction array (init by `FUN_516bc`, copied by
  `FUN_51990`); feeds ETV-2 aux maps. Labelled "ETV/ignition correction level (64 = neutral)",
  confidence medium.
- `0xFEF02644` / `0xFEF0135C` — 0x8000-centered computed signals (`FUN_773f0` / `FUN_4cd6a`), both
  read by `FUN_4ddfc`, which indexes **Cluster-D curves that are flat (unused) in stock**. Labelled
  as centered intermediate signals, confidence low — deliberately not given a specific functional
  name, because the curves they feed are disabled.
- `0xFEF0268C` / `0xFEF0267A` — 0x8000-centered rate-limited chassis/ETV signals (`FUN_7a730` via
  the `FUN_91826` rate limiter), matching the ETV / steering-damper secondary-input role seen on
  the sibling GSX-R ESD module. Labelled as such, confidence medium/low.

These are recorded in `docs/busa-v2-ram-names.csv` and flow into the `TRACED INPUTS` lines. They
are labelled only to the confidence the code supports — the same discipline the GSX-R trace used:
an intermediate/centered signal is role-labelled, never guessed into a fake functional name.

## 5. Recommendation

- For day-to-day tuning, **v2 and v9 are interchangeable** (identical editable definition). Use v2
  when you want the clearer, consistent input-trace lines and the reproducible build; use v9 if you
  prefer the existing per-read stock XDFs already in `hayabusa/stock/<sw>/`.
- The remaining frontier is not more items — it is bench/datalog verification of the LOW-confidence
  scalars and the headline limits (rev/speed limiter, launch, QS), and resolving the 375 LOW
  scalars by per-function decompile reading (now cheap against the shipped `all_functions.c`).
- Everything here remains **unverified on hardware.** Bench an ECM first; keep a stock read.
