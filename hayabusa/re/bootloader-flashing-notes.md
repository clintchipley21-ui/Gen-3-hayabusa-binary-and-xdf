# Bootloader & flashing analysis — working notes (5JCUSJ40 full dump)

Groundwork for a flashing solution, from the first complete, decrypted read
(`stock/other/5JCUSJ40-full.bin`). Items marked **[Ghidra]** are the targets to resolve once
the RH850 decompile of the full dump is available (`tools/ghidra_export_fulldump.py`,
`gsxr-1000/tools/DisasmBoot.py`).

## Silicon & boot firmware (from the boot block, 0x0–0xFFFF — new in this dump)

- MCU: **Renesas RH850/F1L** (device-ID table at 0xC5C8: `R7F701201/202/204/205/206`, `R7F701Z04–Z07`).
- On-chip boot: **Primary Boot Loader** `PBL_RH_TMC_010B_S Ver1.40r2` (0x20), `mPBL_DUMMY Ver1.10r1` (0x40).
  PBL program code occupies ~0x02800–0x0DC20 (~46 KB). This is the Renesas standard
  serial/FP reprogramming firmware — the path Renesas Flash Programmer (RFP3) used to produce
  the `.mot`. Bench reflash of the whole 2 MB already works through it.
- Boot header 0x0–0x1F: word[0]=0x00003764, word[7/0x1C]=0x00003AF0 (PBL entry pointers);
  0x10 validity marker `AC 35 53 CA / A5 5A 5A A5 / A5 5A 5A A5` (Renesas ID/blank-check pattern).
- 0xFFFC holds `16 EE D1 3C` — present only in the full dump (candidate boot-block checksum). **[Ghidra]**
- Application entry at **0x10000** (`e0 57 40 10 90 52 61 52 …`); byte-identical to the 5JCZ reads, so the
  reset/startup stub is shared family-wide even though the rest of the code diverges.

## Integrity fields (what a modified bin must satisfy)

| Field | Location | Covers | Status |
|---|---|---|---|
| **Field 1** | value @0x1FFAFE (BE u16) | CRC-16/CCITT-FALSE over 0x10000–0x1FFAFB | **SOLVED** — `tools/fix_field1_crc.py`; verified on the full dump (computed **0xE29A** == stored). |
| **Field 3** | value @0x1FFEF8 (u32) | ends at 0x1FFEF7 (descriptor `00 00 01 00  F7 FE 1F 00`) | **UNSOLVED** — not a stock CRC32/sum/xor over the obvious ranges (tested). **[Ghidra]** find the compute/verify routine. |

Field-3 record layout (mirrors field-1): `00 00 01 00` flags · `F7 FE 1F 00` = end addr 0x1FFEF7 ·
`<u32 value>` · `NN 00 00 00`. The trailing byte **NN is a reflash/revision counter**:
5JCUSJ40=**0x04**, 5JE0SJ00=**0x02**, 5JCZSJ10/40=**0x01**.

Per-bin field-3 values (LE): 5JCU `0x517CFDE6`, 5JE0 `0x3CEA6DFD`, SJ10 `0x76F5438E`, SJ40 `0x8338BA54`.

## Flashing-solution plan (once Ghidra is on the full dump)

1. **PBL validation path [Ghidra]** — disassemble 0x0/0x3764/0x3AF0 and 0x10000 (DisasmBoot.py).
   Determine what the PBL checks before jumping to the app: just the `A5 5A` marker + a CRC, or a
   cryptographic signature. This decides whether a re-CRC'd modified bin boots at all.
2. **Field-3 algorithm [Ghidra]** — locate the routine that reads 0x1FFEF8 / the 0x1FFEF0 descriptor
   and reproduce it, so a tuned bin gets a valid field-3 (add to `fix_field1_crc.py`). Likely the
   startup self-check; if the app halts/sets a DTC on a bad field-3, this is mandatory for tuning.
3. **Any other runtime checksums [Ghidra]** — cross-ref the field value addresses and the cal region
   for secondary sum checks the app runs periodically.
4. **On-vehicle (OBD/UDS) reflash [Ghidra]** — if bench flashing is to be avoided: find the UDS
   (ISO 14229) handlers in the app — session control (0x10), **security access seed/key (0x27)**,
   routine control erase (0x31), request/transfer download (0x34/0x36/0x37). The seed→key algorithm
   is the gate; recover it from the 0x27 handler. The reflash counter (above) is likely bumped here.

## Already usable today (bench path)

Edit calibration with the new XDFs → `tools/fix_field1_crc.py` (field-1) → write the 2 MB image with
RFP3 over the Renesas serial interface. Open risk until step 2/3: **field-3 is not recomputed**, same
caveat as every bin in this repo. Validate on a bench ECM and keep a stock read for recovery.
