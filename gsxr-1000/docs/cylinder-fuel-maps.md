# Per-cylinder fuel maps: why the GSX-R labels were scattered (and the fix)

This answers the question: *"in the GSX-R XDF we have TPS in-gear Cyl 2 and Cyl 4 (spare 1-4
unused), what about Cyl 1 and Cyl 3, and why is Cyl 4 unused? Same with IAP in-gear: Cyl 1 and 2
but no 3 and 4."*

## Short answer

Nothing is missing on the bike. The **Hayabusa** definition is complete and correct; the **GSX-R**
labels were a porting artifact, now corrected.

## The two fuel banks differ in size

Both ECUs store the fuel maps as a contiguous block of 16-bit 2-D descriptors. But the banks are
different sizes:

| | IAP maps (30×50) | TPS maps (26×50) | total | layout |
|---|---|---|---|---|
| **Hayabusa** | 28 | 28 | **56** | per cylinder: main + blend + 4 spare (6 each) × 4 cyl (24) + Neutral/Clutch × 4 (4), for each of IAP and TPS |
| **GSX-R M7** | 8 | 8 | **16** | per cylinder: 1 map × 4 cyl In-Gear (4) + 4 cyl Neutral/Clutch (4), for each of IAP and TPS — **no blend/spare maps** |

So the Hayabusa carries 6 maps per cylinder (a main map, an inactive "blend" map, and four unused
"spare" slots); the GSX-R carries just one map per cylinder per condition. The GSX-R simply does
not have the blend/spare maps.

## Why the labels scattered

The GSX-R XDF is built by porting the Hayabusa map definitions onto the GSX-R's own descriptors,
aligning the two descriptor lists by **sequence order** (`difflib`). Because the GSX-R fuel block
has 16 maps where the Hayabusa has 56, the order-alignment slipped inside the block: it matched a
few runs and dropped the rest, so the Hayabusa's labels landed on the wrong GSX-R maps — IAP Cyl 1
(all 6 Hayabusa slots) then Cyl 2 (partial), TPS only "Cyl 4 | Spare 1-4", Cyl 3 "missing", and so
on. Every one was already tagged `[UNCONFIRMED]` because the breakpoints differ from the Hayabusa.

That is the artifact you saw. It was never a real gap in the tune — just mis-applied labels.

## Confirmed from the code (not just the shapes)

Three independent lines of evidence, all from the GSX-R's own bin:

1. **One pointer array at `0x1560E4`.** The 16 fuel maps are addressed through a single contiguous
   LE pointer array: entries 0-7 → the 8 IAP maps (`0x157084,0dc,134,18c,1e4,23c,294,2ec`), entries
   8-15 → the 8 TPS maps (`0x15733c,38c,3dc,42c,47c,cc,51c,56c`). Within each 8-map half the array
   order is the first four then the last four.
2. **The readers differ by group.** The GSX-R fuel maps are read by the *same shared functions* as
   the Hayabusa (same code addresses). The first four TPS maps are read by the in-gear base-fuel
   lookup **`FUN_0004536C`**; the last four by the **neutral finaliser `FUN_0004543E`** — the
   function that, in the Hayabusa decompile, selects the neutral/clutch fuel block only when the
   **neutral/clutch flag `0xFEF0271D` bit 0** is set (with vacuum ≥ ~0 kPa and RPM below a gate).
   So first-four = In-Gear, last-four = Neutral/Clutch, proven by which routine reads them.
3. **Z-data decode agrees.** Within maps 0-3 the Z-means are near-identical (IAP
   1043/1052/1036/1047; TPS 1508/1513/1468/1497) and within 4-7 likewise (IAP 1027/1030/1017/1024),
   with a steady offset between the groups — four cylinders × two conditions. Axes decode as
   expected: IAP = manifold vacuum (30 pts) × RPM (50 pts, 800-16000), TPS = throttle angle (26
   pts) × RPM.

The Hayabusa lays In-Gear before Neutral/Clutch in address order (verified: in-gear `0x155a40` <
neutral `0x156280`), and the GSX-R pointer-array order + readers match that, so the identities are
settled.

## The fix (applied, in the generator)

`tools/make_gsxr_xdf.py` relabels the 16 fuel descriptors by structure (function `relabel_fuel`,
keyed by descriptor address), so a regenerate keeps the fix:

- IAP 30×50 @ `0x157084,0dc,134,18c` → **IAP In-Gear Cyl 1-4**; `0x1571e4,23c,294,2ec` → **IAP
  Neutral/Clutch Cyl 1-4**.
- TPS 26×50 @ `0x15733c,38c,3dc,42c` → **TPS In-Gear Cyl 1-4**; `0x15747c,cc,51c,56c` → **TPS
  Neutral/Clutch Cyl 1-4**.

**In-Gear vs Neutral/Clutch and the IAP/TPS type are code-proven** (pointer array + readers +
neutral flag), so the `[UNCONFIRMED]` tag is dropped. The only residual is the exact **cylinder
number** within each group of four (assigned by array position — cylinders are near-identical, so
this can't be separated from the data); each map carries a `CORRECTED LABEL (v2, code-confirmed)`
note stating this, and the values are still GSX-R-specific so verify on a bench.
(`tools/enhance_gsxr_xdf.py` adds the value legends and detects the generator's note, leaving the
fuel labels alone.)

## Takeaway for the generator

`make_gsxr_xdf.py`'s global sequence-alignment is unreliable wherever the GSX-R bank size differs
from the Hayabusa's (the fuel block is the clearest case). The robust approach is to align
same-shape map runs by structure within their block — now done for the fuel maps; other
size-mismatched blocks could be handled the same way if found.
