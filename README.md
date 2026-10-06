# Suzuki Gen-3 ECU — binaries and TunerPro XDFs

Reverse-engineered calibration files for Suzuki motorcycles on the Renesas RH850 (V850E3) ECU
family. Each model lives in its own folder, self-contained and navigable:

| Folder | Model | What's inside |
|---|---|---|
| [`hayabusa/`](hayabusa/) | Hayabusa Gen 3 (2022+, `32990-10Lxx` / `32920-10Lx`) | 8 stock 2 MB reads + per-read XDFs, a full stock master XDF, a custom "race" speed-density + anti-lag build, the Ghidra decompilation (`re/`), docs, and tools. |
| [`gsxr-1000/`](gsxr-1000/) | GSX-R1000 / R, "M7" (`32990-48L00/10/20/30`) | 4 stock 2 MB reads + an XDF for each (791 maps ported from the Hayabusa via the on-bin descriptors + 3,287 scalars found by decompiling the GSX-R), docs, and tools. |

Start with each folder's own `README.md` — [`hayabusa/README.md`](hayabusa/README.md) and
[`gsxr-1000/README.md`](gsxr-1000/README.md).

## How they relate

Both ECUs are the same Suzuki family: identical map-descriptor format, identical field-1 CRC
(CRC-16/CCITT-FALSE over `0x10000–0x1FFAFB`, big-endian at `0x1FFAFE`), and the same four/eight-way
per-market variant structure. The GSX-R XDFs are built by porting the Hayabusa's map definitions
onto the GSX-R's own descriptors, so `gsxr-1000/`'s generator reads reference data from `hayabusa/`
(the Hayabusa master XDF and its decompilation). Everything else in each folder stands alone.

> **Everything here is unverified on hardware.** Bench an ECM first and keep a stock read for
> recovery. See [NOTICE.md](NOTICE.md) for provenance and licensing.
