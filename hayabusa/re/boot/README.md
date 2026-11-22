# Hayabusa Gen‑3 ECM bootloader (PBL) — Ghidra decompile

Reverse engineering of the **Renesas Programmable Boot Loader (PBL)** that ships
in the Gen‑3 Hayabusa ECM flash. Source file:

```
stock/ECM-010L0-0_32990-10L4.mot      (Motorola S‑record, created by Renesas Flash Programmer)
```

The `.mot` is a full 2 MB device image (`0x00000000–0x001FFFFF`, dense, no gaps).
The sibling `32990-10L0_00001_5JE0SJ00_MF.bin` is **app region only**
(`0x1F0000` bytes = `0x00010000–0x001FFFFF`) and does **not** contain the boot
block — so the `.mot` is the only stock artifact that carries the bootloader.

## Boot block — memory map

The bootloader occupies the **first 64 KB** of flash, which the application
dumps omit:

| Range | Contents |
|---|---|
| `0x00000–0x0000F` | Reset / option-byte configuration words (`64 37 00 00 00 01 01 10 …`) |
| `0x00010–0x0001F` | Option bytes / ID-code area (`A5 5A 5A A5` guard patterns) |
| `0x00020` | PBL signature string **`PBL_RH_TMC_010B_S Ver1.40r2`** |
| `0x00040` | Secondary marker **`mPBL_DUMMY Ver1.10r1`** |
| `0x01000–0x010FF` | Interrupt / dispatch vector table (16‑byte entries) |
| `0x01000–0x0DCFF` | PBL code (reprogramming protocol, flash driver, state machine) |
| `0x0C5C8–0x0C62F` | Supported-device table: `R7F701201/202/204/205/206`, `R7F701Z04–Z07` (Renesas **RH850** device IDs) |
| `0x0FFE0` | ECM part-number stamp **`ECM-010L0-0`** |

This boot block differs from the older `5JCZSJ40` image in **47,661 of 65,536
bytes**, i.e. it is a genuinely different/newer bootloader build.

## Processor

- **Renesas RH850** (G3 core, V850E3V5 ISA), little‑endian, 32‑bit.
- Ghidra language id: `RH850:LE:32:default` (community *Ghidra‑RH850* SLEIGH module).
- Load base `0x00000000`. RAM (`0xFEBF0000+`) and peripheral/SFR
  (`0xFF000000+`) windows added as uninitialized blocks so data references resolve.

## Results

Auto-analysis found and decompiled **193 functions** inside `0x0–0xFFFF`
(100 % decompiled). The code is the expected PBL: a serial reprogramming
protocol handler with a command/response state machine, erase/write flash
routines, and the device-ID gatekeeping table above.

## Folder contents

| File | What it is |
|---|---|
| `boot_10L4.bin` | Raw 64 KB boot block extracted from the `.mot` (`0x0–0xFFFF`) |
| `boot_decompiled.c` | Decompiled C for all 193 boot-block functions |
| `boot_functions.csv` | `entry, name, size, calling_conv` for each function |
| `ghidra-boot.zip` | The Ghidra project (`busa_boot`) — open in Ghidra to browse/annotate |

## Reproduce

Requires **Ghidra 12.2** (needs **JDK 25+**) and the **Ghidra‑RH850** SLEIGH
module.

```sh
# 1. Install the RH850 language module into the Ghidra install and (re)compile it
#    (the module ships a 2022 .sla; Ghidra 12.2 uses a newer compressed .sla format)
cp -r Ghidra-RH850-main/{Module.manifest,data} $GHIDRA/Ghidra/Processors/RH850/
rm $GHIDRA/Ghidra/Processors/RH850/data/languages/RH850.sla
$GHIDRA/support/sleigh.bat $GHIDRA/Ghidra/Processors/RH850/data/languages/RH850.slaspec

# 2. Convert the S-record to a raw image and slice the boot block
python srec2bin.py ECM-010L0-0_32990-10L4.mot 10L4-full.bin   # 2 MB, 0x0..0x1FFFFF
#    boot block = first 0x10000 bytes  ->  boot_10L4.bin

# 3. Headless import + analysis + export (base 0x0, RH850 language)
$GHIDRA/support/analyzeHeadless.bat <projDir> busa_boot \
    -import boot_10L4.bin -processor RH850:LE:32:default \
    -preScript  AddBootBlocks.java \
    -postScript ExportBootDecomp.java <outDir>
```

`AddBootBlocks.java` adds the RAM/peripheral blocks; `ExportBootDecomp.java`
decompiles every function with an entry in `0x0–0xFFFF` and writes
`boot_decompiled.c` + `boot_functions.csv`. Both scripts are in `tools/ghidra/`.
