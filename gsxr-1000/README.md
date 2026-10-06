# Suzuki GSX-R1000 (M7) — binaries and XDF

Suzuki GSX-R1000 / GSX-R1000R, "M7" generation ECM (Renesas RH850, same family as the Gen 3
Hayabusa in the parent repo). Four stock 2 MB reads and a TunerPro XDF for each. The maps/curves are
ported from the Hayabusa definitions via the GSX-R's own on-bin map descriptors; the scalar
constants/flags were recovered by decompiling the GSX-R code in Ghidra. Each XDF has 4,078 items.

> **Everything here is unverified on hardware, and the map *labels* are ported from a different
> model (the Hayabusa) — they are informed guesses, not confirmed on this ECU.** Bench an ECM
> first, keep a stock read for recovery, and log before you trust any value.

## What's here

```
M7/
  32990-48L00.bin / .xdf      base read + its XDF
  32990-48L10-US.bin / .xdf   US read   (19 bytes different from 48L00: IDs, 2 flag bytes, checksums)
  32990-48L20-EU.bin / .xdf   EU read   (~4,100 calibration bytes different from 48L00)
  32990-48L30.bin / .xdf      read      (~4,100 calibration bytes different from 48L00)
  <service manuals / SDS / pinout PDFs live in Dropbox, not committed here — see "Reference material">
tools/
  make_gsxr_xdf.py            regenerates an XDF from a read (descriptor + scalar driven; see below)
  extract_scalars.py          rebuilds docs/scalars.json from the Ghidra cal-xref dumps
  DumpCalXrefs.py             Ghidra headless postscript: dump code->calibration references
docs/
  map-index.csv               every map in the XDF: confidence, title, dims, address, axes, values
  scalar-index.csv            every decompiler-discovered scalar: address, width, value, refs, context
  scalars.json                the scalar list the generator injects (addresses are variant-independent)
```

Build ID embedded in the reads: `8J16ST01` (`ECM-010L0`). All four reads are full 2 MB and have a
valid field-1 CRC. Each XDF is ~3.3 MB with **4,078 items** (791 maps/curves + 3,287 scalars/flags);
if TunerPro is slow to open it, regenerate without scalars by renaming `docs/scalars.json`.

## How to use it in TunerPro

1. Open the `.xdf` that matches your read (e.g. `32990-48L20-EU.xdf` for `32990-48L20-EU.bin`).
2. Load the matching `.bin`.
3. After editing, re-stamp the checksum:
   `python3 tools/fix_field1_crc.py your-tuned.bin` — the parent repo's tool works on these reads
   **unchanged** (identical CRC method; verified on all four).

One XDF per read is provided, but the map layout (addresses, sizes, axes) is identical across all
four reads, so any of these XDFs will open any of the four reads; only the stock-value text in the
descriptions is read-specific.

## How the XDF was built (and what "confidence" means)

The M7 ECU stores the same Suzuki **map-descriptor table** the Hayabusa does — 20-byte records
holding a type, column/row counts and little-endian pointers to each map's data and axes. The
generator (`tools/make_gsxr_xdf.py`):

1. scans the GSX-R read for its descriptors — **791** maps/curves found (the identical scanner
   recovers all 749 Hayabusa descriptors exactly, so it is trusted);
2. aligns that descriptor list to the Hayabusa's by calibration order and shape;
3. reuses the matching Hayabusa map's **exact** XDF definition (bit size, scaling, units, folders)
   and swaps in the GSX-R addresses.

Each map is tagged by how sure the match is:

| Confidence | Count | Meaning |
|---|---:|---|
| **HIGH** | 420 | GSX-R and Hayabusa axis breakpoints are byte-identical — almost certainly the same map. |
| **MED** (`[UNCONFIRMED]` in the title) | 234 | Same type/size and aligned by order, but breakpoints differ — a strong guess; **verify before trusting**. |
| **GENERIC** (`Unknown Map/Curve …`) | 137 | No Hayabusa counterpart; auto-discovered, address/size/axes are real but the role is unknown. |

`docs/map-index.csv` lists all 791 so you can review the MED and GENERIC ones. Scaling and units
are carried over from the Hayabusa and are **unverified on this ECU** — the sensors and ADC scales
are likely shared across the platform, but confirm against the service data before relying on them.

Each ported map also carries an **INPUTS (Hayabusa decompile)** line in its description, giving the
X/Y signal meaning (engine RPM, throttle position, IAP, gear/mode index, …) and the Hayabusa
function that reads it. That metadata comes from the parent repo's decompilation
(`re/decompiled.zip` → `map_links.csv`) and is a strong hint, not a GSX-R-verified fact.

### Validation (quadruple-check pass)

The descriptor set and all four XDFs were checked exhaustively:

- **Completeness** — a full-image descriptor sweep (`0x10000–0x1FF000`) finds no real map outside
  the `0x150000–0x1C0000` calibration window. One spurious hit inside the code region (`0x103D0`)
  is a false positive — its "axis" is non-monotonic garble — and is correctly excluded.
- **Structure** — of 791 maps: **0** Z-data regions out of bounds, **0** Z-data regions overlap a
  neighbour, **0** category references unresolved, **0** duplicate IDs; every XDF is well-formed XML.
- **Cross-variant** — all four reads have a byte-for-byte identical descriptor layout (addresses,
  sizes, axis pointers), so any one XDF opens any of the four reads.
- **Sanity flags** — 310 maps are flat (every cell identical: unused/disabled in stock, as on the
  Hayabusa); 27 maps have a non-monotonic X axis (2 HIGH — byte-identical to proven Hayabusa maps,
  so a genuinely non-sorted axis; 20 MED and 5 GENERIC — already flagged for review).
- **HIGH spot-checks** — decoded maps read physically (RPM × gear-bit quickshifter durations,
  ignition-retard-vs-TP-angle, accel-enrichment vs IAT in °C, etc.).

## Scalar constants and flags (from decompiling the GSX-R)

Beyond the descriptor-backed maps, the XDF now contains **3,287 scalar constants/flags** — the
individual calibration values (limiter thresholds, gates, enable bytes, gains) that have no map
descriptor. These were found by **decompiling the GSX-R's own code** and taking cross-references:

- Each read was analysed in **Ghidra headless** with processor `V850:LE:32:default` (the RH850 G3
  core is the V850E3; base V850 decodes the standard address-forming code, leaving only a handful of
  RH850-only instructions undecoded), base address `0x0`, via `tools/DumpCalXrefs.py`.
- A "scalar" is a calibration address (`0x150000–0x1B0000`) that code **loads or stores** but which
  is **not** inside any map descriptor's data/axes span. `tools/extract_scalars.py` derives them and
  records width (from the load mnemonic: `ld.bu`→u8, `ld.hu`→u16, `ld.w`→u32), value, reference
  count, the reading function, and a **context hint** — the named (Hayabusa-ported) maps the same
  function also reads.
- **Validation:** run on the Hayabusa reference read, this method recovers **96%** of the master
  XDF's known constants/flags as scalars (≈99% of those inside the calibration region), so the
  GSX-R scalar set is near-complete.

In TunerPro they appear under **"ZZ Decompiler-discovered scalars (unverified)"**, titled generically
(`Scalar @0xADDR (u16)`, `Flag @0xADDR (bit7)`) because no Hayabusa label aligns to a bare scalar
reliably; the description carries the value, usage and context hint. Treat every one as a lead to
confirm, not a known setting. `docs/scalar-index.csv` lists them all (351 carry a context hint).

## Regenerating

```
python3 gsxr-1000/tools/make_gsxr_xdf.py M7/32990-48L00.bin M7/32990-48L00.xdf 32990-48L00 32990-48L00
```

The tool reads the Hayabusa master (`../stock/master/master-v9.xdf`) and reference read
(`../stock/5JCZSJ10/5JCZSJ10.bin`) from the parent repo to source the definitions.

## Checksums

- **Field 1**: CRC-16/CCITT-FALSE over `0x10000–0x1FFAFB`, stored big-endian at `0x1FFAFE` — the
  same method as the Hayabusa, confirmed valid on all four reads. Re-stamp with
  `tools/fix_field1_crc.py`.
- **Field 3** (`0x1FFEF8`): not solved, not recomputed — same open question as the parent repo.

## Reference material

The Dropbox `Gsxr-1000/M7/` folder also holds the Suzuki GSX-R1000 A/R (L7-/M7-) service manual
ECU-pinout PDFs, the 2027 specification and service-data sheets, and the SDS-II model list. Those
are Suzuki's copyrighted documents and are **not** committed to this repo; keep them alongside in
Dropbox. The pinout and service data are useful for confirming sensor scalings on the MED/generic
maps.

## Next steps to raise confidence

1. **Label the scalars.** They are discovered and valued but titled generically. The highest-value
   next step is matching the headline ones (rev/speed limiters, launch RPMs, quickshifter/traction
   enables) to their role — start from the 351 with a context hint and from the reading function's
   decompiled C, or align per-function scalar lists to the Hayabusa master more aggressively.
2. Review `docs/map-index.csv`; sanity-check the 234 MED titles against the maps' axes and values.
3. Confirm sensor scalings (RPM, TPS/ETV angle, pressure, temperature) against the GSX-R service
   data — if any differ from the Hayabusa, update the ported equations.
4. Deepen the decompile: an RH850-accurate Ghidra processor variant (the `v850e3v5` the parent
   project used) would decode the handful of instructions base V850 misses and push scalar/xref
   coverage above the current 96%.
