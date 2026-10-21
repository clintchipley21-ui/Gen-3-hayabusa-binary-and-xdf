# Patch verification — rolling anti-lag + auto-upshift (air-shifter)

Verification of the two code patches whose tuning items the v2 Hayabusa XDFs expose
(folder **"22 Patches & Air-Shifter"**). Applied with `../../tools/apply_patches.py`; sources in
`../../race/als/` (`als.s`, `autoshift.s`), assembled blobs `autoshift.bin` (and the anti-lag bytes
carried in `../../race/Busa-SD-v4.1.bin`).

> **Still UNVERIFIED on hardware.** These checks prove the patch applies cleanly, is structurally
> correct, and matches the XDF — not that it behaves as intended on a running ECU. Bench first.

## 1. Apply + checksum + region containment (on 5JCZSJ40)

`apply_patches.py stock.bin out.bin` (both patches):

- Applies cleanly: **9 regions** (anti-lag 6, auto-upshift 3), output is exactly 2 MB.
- **Field-1 CRC re-stamped and valid** — recomputed CRC-16/CCITT `0xDD10` == stored `0xDD10`.
- **Only the expected regions differ from the stock read**, nothing stray:

| Region | Bytes | What |
|---|---:|---|
| `0x02C700` | 4 | anti-lag hook |
| `0x0525F2` | 4 | anti-lag hook |
| `0x05BE02` | 4 | anti-lag hook (→ ALS_TICK) |
| `0x05DC9E` | 4 | auto-upshift hook (→ AUTOSHIFT_TICK) |
| `0x0BE000–0x0BE27D` | 638 | ALS code (0xBE000) + auto-upshift code (0xBE148), adjacent |
| `0x0BF000–0x0BF021` | 34 | anti-lag cal (0xBF000, 16B) + auto-upshift cal (0xBF010, 18B) |
| `0x188214–0x18858F` | 892 | anti-lag ignition-retard map |
| `0x1FFAFE` | 2 | field-1 CRC |

- **Idempotent:** `--check` reports "to apply" on a stock bin and "already present" on a patched bin.

## 2. Hooks decode correctly (V850 `jarl disp22`)

Each hook replaces one `jarl` with a `jarl` into the patch code; the patch trampolines back through
the original target so stock behaviour is preserved.

| Hook @ | Stock target | Patched target | Into |
|---|---|---|---|
| `0x5DC9E` | `jarl 0x5DB5E` (PAIR/EVAP output mapper) | `jarl 0xBE148` (AUTOSHIFT_TICK), r31 | auto-upshift |
| `0x5BE02` | `jarl 0x5BDB4` | `jarl 0xBE000` (ALS_TICK), r31 | anti-lag |
| `0x2C700` | `jarl 0x2C720` | `jarl 0xBE0D6` | anti-lag |
| `0x525F2` | `jarl 0x7446A` | `jarl 0xBE138`, r31 | anti-lag |

`AUTOSHIFT_TICK` calls `FUN_5DB5E` first (runs the stock mapper), then applies its pulse, then
returns via `dispose 0,{lp},[lp]` to `0x5DCA2` — so the displaced call still happens and the stock
output is preserved; the patch only has the last word on the output for that cycle.

## 3. XDF items ↔ applied calibration

All **19** patch items in the XDF fall inside the applied cal (`0xBF000–0xBF021`), and decoding the
patched bin through each item's own equation yields the intended defaults in the right units:

- **Auto-Shift:** Enable `0x00` (OFF), Bench Test `0x00`, Pulse `20` ticks, Min Grip `30.0°`,
  Re-arm `500` rpm, Targets 1→2…5→6 `9500` rpm.
- **Anti-lag (ALS):** Enable `0x00` (OFF), Min Coolant `60 °C`, Min Rolling Speed `20 km/h`,
  Capture Grip `90°`, Release Grip `60°`, Min Capture `3000` rpm, Max Capture `10500` rpm,
  Hysteresis `150` rpm, Max Active `10.0 s`.

Both features **ship disabled** (enable bytes `0x00`), as intended.

## 4. Reassembly from source (byte-for-byte reproducible)

Built GNU binutils 2.43 for `v850-elf` from source (gas/ld/objcopy, `-mv850e3v5`) and reassembled
the patch sources exactly as `../../race/als/build.sh` specifies:

| Source | Rebuilt | Committed / in-bin | Result |
|---|---|---|---|
| `autoshift.s` → `.as_code` @0xBE148 | 310 B | `race/als/autoshift.bin` (310 B) | **byte-identical** (same SHA-256) |
| `als.s` → `.als_code` @0xBE000 | 328 B | anti-lag code in `race/Busa-SD-v4.1.bin` @0xBE000 (328 B) | **byte-identical** (same SHA-256) |
| auto-shift hook `jarl AUTOSHIFT_TICK` @0x5DC9E | `86ffaa04` | `apply_patches.py` `AS_HOOK` = `86ffaa04` | **matches** |

So the committed patch blobs and the hook word are exactly what the assembly sources produce — the
binary patches contain no bytes the source does not account for.

**Emulator run:** not performed (the GDB `v850` simulator needs GMP/MPFR dev headers that aren't
available in this sandbox, and the user opted to skip it). The logic was instead confirmed statically
— hook/trampoline decode (§2), cal layout vs XDF (§3) — and the anti-lag code is the already
field-exercised `Busa-SD-v4.1` build.

## Limits (what these checks do NOT cover)

- **Hardware behaviour** — unverified on a running ECU.
- **Auto-shift output pin/polarity** — `autoshift.s` flags the `OUT_ON/OUT_OFF` bits
  (`fef020e1` bit0 / `fef020e0` bit2) as a *candidate*; confirm on the bench with the XDF
  **"Bench Test Output"** switch before trusting the shift output.
