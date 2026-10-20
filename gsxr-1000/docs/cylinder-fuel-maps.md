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

## Confirmed by decoding the map data

Decoding the Z-data of the 16 maps confirms the structure (not just a guess from shapes):

- Within maps **0-3** the Z-means are near-identical (IAP 1043/1052/1036/1047; TPS
  1508/1513/1468/1497) and within maps **4-7** likewise (IAP 1027/1030/1017/1024) — i.e. each
  group of four is **four cylinders of one condition**.
- The two groups of four differ by a small, consistent offset — i.e. **two conditions**.
- Each map has its own X/Y axes: IAP = manifold vacuum (X, 30 pts) × RPM (Y, 50 pts, 800-16000);
  TPS = throttle angle (X, 26 pts) × RPM (Y) — the expected fuel-map axes.

So the layout is **4 cylinders × 2 conditions**, block-by-condition. The Hayabusa lays its In-Gear
block before its Neutral/Clutch block (verified: in-gear `0x155a40` < neutral `0x156280`), so the
GSX-R's first four are labelled In-Gear and the last four Neutral/Clutch.

## The fix (applied, in the generator)

`tools/make_gsxr_xdf.py` now relabels the 16 fuel descriptors by structure (function `relabel_fuel`,
keyed by descriptor address), so a regenerate keeps the fix:

- IAP 30×50 @ `0x157084,0dc,134,18c` → **IAP In-Gear Cyl 1-4**; `0x1571e4,23c,294,2ec` → **IAP
  Neutral/Clutch Cyl 1-4**.
- TPS 26×50 @ `0x15733c,38c,3dc,42c` → **TPS In-Gear Cyl 1-4**; `0x15747c,cc,51c,56c` → **TPS
  Neutral/Clutch Cyl 1-4**.

The **4-cylinder × 2-condition split and the cylinder grouping are data-confirmed**; the
**in-gear-vs-neutral identity and the cylinder numbering are by platform layout order**, so every
map stays `[UNCONFIRMED]` and carries a `CORRECTED LABEL (v2)` note saying exactly this — confirm by
logging. (`tools/enhance_gsxr_xdf.py` still adds the value legends; it detects the generator's note
and leaves the fuel labels alone.)

## Takeaway for the generator

`make_gsxr_xdf.py`'s global sequence-alignment is unreliable wherever the GSX-R bank size differs
from the Hayabusa's (the fuel block is the clearest case). The robust approach is to align
same-shape map runs by structure within their block — now done for the fuel maps; other
size-mismatched blocks could be handled the same way if found.
