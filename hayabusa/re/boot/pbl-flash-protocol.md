# Gen‑3 Hayabusa flash path — what the PBL decompile tells us

Consolidated findings from decompiling the new `ECM-010L0-0_32990-10L4.mot`
boot block, cross‑referenced with the confirmed app‑side analysis in CalStudio's
`busa_ecu_util.py`. Written to feed a standalone CAN flasher.

## The two protocol layers (now resolved)

| Layer | Where it lives | Protocol | Status |
|---|---|---|---|
| **Diagnostics / scanner / live data** | Application (`0x10000+`) | **KWP2000‑over‑CAN**, request ID **`0x7B0`** → response **`0x7B1`**, CAN‑C @ `0xFFE60000` | Confirmed in app code (`busa_ecu_util.py`): RX dispatch `FUN_ram_0008d77e`, TX `FUN_ram_0008d9fc` |
| **Flashing (erase/write)** | **Boot loader** (`0x0–0xFFFF`, this PBL) | **Renesas‑proprietary programming protocol — NOT UDS** | Decompiled here; command set partly mapped; **auth unsolved** |

The key correction this decompile makes to the earlier model: the app has **no
flash service** (no `0x34/0x36/0x37`), and the PBL does **not** implement UDS
either. Flashing is the **Renesas boot‑loader protocol**, entered from the
diagnostic session (or a boot‑mode strap). A UDS `0x34`/`0x36`/`0x37` flasher
will not drive this ECU's write path — the boot‑loader command set does.

## The PBL (boot block `0x0–0xFFFF`)

- Signature `PBL_RH_TMC_010B_S Ver1.40r2`; secondary `mPBL_DUMMY Ver1.10r1`.
- 193 functions, Renesas RH850 / V850E3V5.
- **Device‑ID gate** (`0x0C5C8`): accepts `R7F701201/202/204/205/206`, `R7F701Z04–Z07`. The dispatcher walks a descriptor table (fields at `+0xbf8…+0xc0f`: entry counts + record pointers) and matches the connected device before allowing operations.
- **CRC‑32 routine** at `0x0C844` (polynomial `0xEDB88320`, reflected) — image/block integrity validation during programming.
- **Option / ID‑code area** at `0x10`: `AC 35 53 CA  A5 5A 5A A5  A5 5A 5A A5  F0 3A 00 00`. The `A55A5AA5` words are the RH850 ID‑authentication pattern.

### Command / status code set (observed in the state machine)

Status/response bytes: `0x90 0xA2 0xA3 0xB1 0xB2 0xB5 0xC9 0xCA 0xD0 0xD2 0xF3 0xF8 0xF9`
Low command/length bytes: `0x10 0x20 0x30`

These are **not** UDS SIDs (no `0x27/0x34/0x36/0x37/0x3E`). The pattern (high‑nibble
status codes + a framed command/length) is characteristic of the Renesas RH850
serial/CAN programming protocol (SOH · length · command · data · checksum · status).
The exact frame layout still needs confirmation from a real flash trace (see below).

## The seed/key — honest status

**Not cracked, and the PBL plaintext does not hand it over directly.** Evidence:

- No AES / inverse‑AES S‑box, SHA‑1/256, or MD5 constant tables in the boot block.
- No `0x27`/SecurityAccess handling (this isn't UDS).
- The authentication is consistent with an **RH850 ID‑code check or a mask‑boot‑ROM
  routine**: the PBL's security‑relevant state uses `gp`‑relative RAM in the
  `0xFFFF8000+` / boot‑ROM‑mirror region, which is not contained in this 2 MB image.
- This matches the earlier conclusion in `seed-key-investigation.md` that the gate
  "lives below the application." The new `.mot` advances the **protocol** a great
  deal but does not, by itself, yield the key.

### Two concrete ways to unlock, in priority order

1. **Test the ID‑code hypothesis (cheapest).** If the gate is the RH850 16‑byte
   ID‑authentication, the unlock value is *stored in the flash we can read* — the
   prime candidate is the `0x10` option area (`AC3553CA A55A5AA5 A55A5AA5 F03A0000`).
   On a bench ECU, send that as the ID and see if programming unlocks. No crypto to break.
2. **Capture one real exchange.** A single seed→key (or ID‑auth) exchange from an
   OEM / MPVI / Tactrix flash session is enough to replay, and several are enough to
   derive the algorithm. **None of the three on‑disk CAN captures contain a flash
   session** (both `.asc` are passive bus sniffs, 0 tester frames; the MPVI xlsx is a
   USB‑enumeration capture). So this needs a *new* capture — which the `capture_flash`
   helper is built to take.

## What the flasher should do with this

- Keep the KWP‑on‑CAN side (`0x7B0/0x7B1`) for identification, session control,
  DTCs, and live data — that part is confirmed and works.
- Model the **write path as the boot‑loader protocol**, not UDS `0x34/0x36/0x37`.
- Treat auth as a **pluggable provider** (`seedkey.py`): ID‑code, static replay, or
  a derived algorithm, selected per what the capture reveals.
- Validate every image with the **Field‑1 CRC** (already solved) and the PBL's
  **CRC‑32** block check before writing; keep Field‑3 untouched (unsolved, likely
  informational).
- **Never write without a verified recovery path** (PBL/bench) and a known‑good
  stock read on hand.
