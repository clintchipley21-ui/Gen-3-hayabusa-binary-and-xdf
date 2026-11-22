# Gen‑3 Hayabusa CAN recon (10L4 full image)

Reverse engineering of the CAN‑bus stack from the full 2 MB `10L4` read
(`ECM-010L0-0_32990-10L4.mot`), cross‑referenced with two live bus captures and
the `hayabusa-gen3.dbc`. Produced from the full‑image Ghidra decompile
(7048 functions; 43 touch the CAN‑C peripheral).

## Headline finding — the ECM speaks standard OBD‑II

The ECM's CAN receive‑filter table (in flash at **`0x00142D48`**) accepts, among
others, **`0x7DF`** (ISO 15765‑4 OBD‑II *functional* broadcast) and **`0x7E0`**
(OBD‑II *physical* request) — so this ECU responds to **generic OBD‑II / UDS on
`0x7E0` → `0x7E8`**, in addition to the Suzuki‑specific diagnostic channel
`0x7B0` → `0x7B1`. That's a second, standards‑based way into the ECU for
identification and (potentially) memory reads, worth trying before anything exotic.

## Transport

- **Controller:** RH850 **CAN‑C**, register base **`0xFFE60000`** (`0xFFE60000–0xFFE61xxx`).
- **Init / config:** `FUN_0001f5b0` and `FUN_0001eb2a` (the most CAN‑C register
  writes); frame RX/TX handlers in the `0x0001bxxx–0x0001exxx` cluster.
- **Mailboxes:** message‑buffer region at `0xFFE61000+`; per‑mailbox RAM data
  buffers mapped at `0xFEBF5Dxx` (pointer table follows the filter table).
- Full register usage in [`can-c-registers.csv`](can-c-registers.csv).

## CAN IDs

Two complementary sources, merged in [`can-ids.csv`](can-ids.csv):

- **`in_fw_filter=1`** — the ID is in the ECM's hardware **receive** filter
  (`0x142D48`), i.e. the ECM *listens* for it. Full table in
  [`can-mailbox-table.csv`](can-mailbox-table.csv).
- **`on_bus=1`** — the ID was seen on the physical bus in the captures (with its
  DLC, frame count, and a per‑byte **dynamic map** `X`=varies `.`=static).

### What the ECM receives (filter table, `0x142D48`)

`0x175 0x179 0x195 0x196 0x1D1 0x231 0x235 0x3B1` (inter‑module) and the
diagnostic channels `0x4D4 0x4D7 0x6A0 0x7B0 0x7DF 0x7E0`. The diagnostic IDs are
**not** on the passive bus — they only appear when a tester is connected, which
is why earlier trace mining never saw them.

### What the ECM transmits

From the captures, ECM‑sourced broadcasts are `0x175 0x179 0x180 0x181` (engine)
and `0x321` (cruise). These are *absent* from the receive filter — consistent
with them being transmit mailboxes, not receive filters.

### Signal structure

Every 8‑byte broadcast frame follows the house pattern: **byte 6 = AliveCounter,
byte 7 = Checksum** (confirmed against the DBC). The `dynamic_bytes` column in
`can-ids.csv` shows which payload bytes carry live signals — the starting point
for decoding the remaining `UNK_*` messages.

## Files

| File | |
|---|---|
| `can-ids.csv` | Merged definition: ID, name, sender, on‑bus, in‑fw‑filter, DLC, frame count, dynamic‑byte map, notes |
| `can-mailbox-table.csv` | The ECM receive‑filter table decoded from flash `0x142D48` |
| `can-c-registers.csv` | Every `0xFFE6xxxx` CAN‑C register the firmware touches, with the functions using it |
| `decompiled-10L4.zip` | Full 10L4 decompile: `all_functions.c` (7048 fns), `can_functions.c` (43 CAN fns, ranked), `function_index.csv` |

## Next steps this opens up

- **Try OBD‑II `0x7E0`/`0x7E8`** with a generic UDS/OBD client (our `capture_flash.py`
  works with `--req-id 0x7E0 --rsp-id 0x7E8`) — may expose `ReadDataByIdentifier`
  / `ReadMemoryByAddress` without the Suzuki‑specific path.
- **Decode the `UNK_*` messages** using the dynamic‑byte maps + the sender modules.
- `0x6A0` has larger buffer config than the 8‑byte broadcasts — likely a
  multi‑frame (ISO‑TP) diagnostic/comms channel worth watching during a tool session.
