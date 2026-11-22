# Hayabusa Gen‑3 CAN flasher (standalone)

A standalone, CalStudio‑ready toolkit for talking to the Suzuki Gen‑3
Hayabusa / GSX‑R1000 ECU over CAN. It builds on the reverse‑engineering in
[`../../re/boot/`](../../re/boot/) (the new `.mot` PBL decompile) and consolidates
the protocol facts already proven in CalStudio's `busa_ecu_util.py`.

> **Status: read/identify + capture work today. ECU *writing* is gated on the
> unsolved auth (seed/key or RH850 ID‑code) — see
> [`pbl-flash-protocol.md`](../../re/boot/pbl-flash-protocol.md).** This toolkit
> is structured so that the moment a capture reveals the gate, writing drops in.

## The protocol, in one paragraph

Diagnostics / scanner / live data run over **KWP2000‑on‑CAN**, request ID
**`0x7B0`** → response **`0x7B1`** (CAN‑C `0xFFE60000`, confirmed in the app).
**Flashing is a different layer** — the **Renesas boot‑loader protocol** in the
PBL we decompiled, *not* UDS `0x34/0x36/0x37`. The write gate (SecurityAccess
seed/key, or an RH850 16‑byte ID‑authentication) lives below the app and is the
one missing piece.

## Files

| File | What it does | State |
|---|---|---|
| `capture_flash.py` | Reassembles ISO‑TP on `0x7B0/0x7B1` from a live CAN bus **or** a Vector `.asc` log; decodes KWP services; extracts SecurityAccess seed→key pairs to a replay file. **Read‑only, never transmits.** | Works |
| `seedkey.py` | Pluggable auth: `ReplayProvider` (captured pairs), `IdCodeProvider` (RH850 ID‑code from the image), `DerivedProvider` (algorithm, once known). | Replay + ID‑code work |
| `busa_ecu_util.py` *(in CalStudio `re/`)* | The existing base: Field‑1 CRC, model/ID detection, KWP‑on‑CAN + K‑line transports, flash skeleton. | Vendor or import |

## Unlock path (do this on a bench ECU, with a stock read on hand)

1. **Try the ID‑code first (no crypto to break).**
   ```
   python3 seedkey.py --image ../../re/boot/boot_10L4.bin
   # -> ac3553caa55a5aa5a55a5aa5f03a0000  (candidate RH850 ID-auth)
   ```
   Feed that as the ID‑authentication to the boot loader; if programming
   unlocks, the "seed/key" was never crypto — it's this stored ID.

2. **Otherwise capture one real exchange.** Run an OEM / MPVI / Tactrix flash
   while sniffing the bus:
   ```
   python3 capture_flash.py --live --channel can0 --bitrate 500000 \
           --json session.json --replay keys.json
   ```
   `keys.json` then feeds `ReplayProvider`. One pair replays a fixed‑seed ECU;
   several pairs let you derive the algorithm into `DerivedProvider`.
   (Offline, point it at a `.asc`: `python3 capture_flash.py trace.asc`.)

## CalStudio integration

- `capture_flash.py` and `seedkey.py` import cleanly — CalStudio's Rust backend
  can shell out to them as a sidecar, or the logic can be ported into
  `desktop/src/lib/protocol/`.
- `seedkey.AuthProvider` is the single seam CalStudio's flasher plugs into; keep
  the write path (boot‑loader protocol) behind it.
- This lives in the `gen-3-hayabusa-binary-and-xdf` data repo that CalStudio
  already references, so the RE artifacts and the tool ship together.

## Requirements

`python-can` for `--live` capture (`pip install python-can`); nothing beyond the
standard library for offline `.asc` decode and `seedkey.py`.

## Safety

This talks to a $1k+ ECU. Validate every image's **Field‑1 CRC** before writing,
leave **Field‑3** untouched, keep a known‑good stock read for recovery, and bench
an ECM with a CKTEST image before touching the bike. Never write without a
verified recovery path (the PBL is that backstop).
