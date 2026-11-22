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

## Scanner integration

`hayabusa-gen3-enhanced.dbc` is your scanner DBC with our findings merged in:

- **+7 diagnostic/comms messages** the ECM filters but your DBC didn't have:
  `OBD_Functional_Request_7DF`, `OBD_Physical_Request_7E0`, `OBD_Response_7E8`,
  `SDS_Request_7B0`, `SDS_Response_7B1`, `COMM_6A0`, `COMM_4D4` (+ a `Tester` node).
- **Firmware-confirmed direction** on every broadcast id (RX-filter vs TX), in the
  provenance comment — so sender guesses in the scaffold can be corrected.

What this adds to the scanner, concretely:

1. **Broadcast decoding.** Your sampler currently *polls* (OBD PIDs on 0x7E0, RAM on
   0x7B0). The bike also *broadcasts* engine/ABS/cluster data continuously (0x175/179/…).
   A DBC-driven broadcast source gives that live data with zero polling — just listen.
2. **OBD-II profile is validated.** Your `suzuki-hayabusa-gen3-obd2` profile (0x7E0→0x7E8)
   is confirmed correct: 0x7DF and 0x7E0 really are in the ECM's hardware receive filter.
3. **Ready-made RAM channel names.** `re/decompiled.zip` already carries ~2,270 labeled
   RAM variables (823 HIGH-confidence) — a large name/definition source for the RAM
   (0x7B0) logging source, beyond what's wired today.

Still a stub: the **engine broadcast signal names** (0x175/179/180/181 payload words).
Naming those needs a decode of the ECM's CAN transmit builders (which sensor RAM fills
each byte) — a focused follow-up, not guesswork.

## Does this help the XDFs?

Mostly no — the CAN recon helps the *scanner*, not the tuning tables. The tuning XDFs
describe fuel/ignition/limit maps, which the CAN stack doesn't touch. The real XDF-detail
lever from this session is different: the **full 10L4 decompile** (`decompiled-10L4.zip`,
7048 functions) is exactly what your `docs/autodef-trace.csv` → `tools/xdf_autodef_trace.py`
pipeline consumes. The existing trace was built from `5JCZSJ40`; regenerating it against
the 10L4 image would refresh/extend the auto-defined item labels for the 10-series XDFs.
That's a substantial tracing pass (the current CSV is ~2,270 rows) — worth doing as its
own step if you want the 10L4 XDFs labeled from current code.

## Global pointer (gp) resolved

The RH850 **global pointer `gp` is 0 at the application level** — the C runtime
never loads it with an immediate, so the compiler's "gp-relative" accesses are
really absolute into the `0xFFFF8xxx` local-RAM region, and the engine sensor
RAM lives at `0xFEF0xxxx` (addressed absolutely). Pinning `gp=0` / `tp=0` in the
decompiler context clears the spurious `+ unaff_gp` term and resolves the RAM
references (e.g. `FUN_00019966`: `iVar2 = uVar3 + unaff_gp; (&DAT_ffff93b8)[iVar2]`
becomes `(&DAT_ffff93b8)[iVar3]`). `decompiled-10L4.zip` is the clean re-decompile;
`tools/ghidra/SetGp0.java` reproduces it (run as a Ghidra preScript before export).

Sensor RAM confirmed at `0xFEF0xxxx`; the Suzuki diagnostic ISO-TP receive buffer
is at `0xFEBF57xx` (`DAT_febf57a8` holds the received CAN id, flow-control `0x30`
checked). Naming the individual engine broadcast signals still requires tracing
each CAN transmit builder to its sensor source (or a correlated bus+PID capture
for ground-truth scaling) — the clean decompile is the prerequisite for that work.

## Engine telemetry naming — why static tracing stalls (and the fix)

Attempted (with gp resolved) to name the engine broadcast signals by tracing the
transmit path. Result: the ECM uses an **AUTOSAR-style COM/PDU stack**, not
hand-packed frames.

- `FUN_0001f81a(descriptor, 1, msg_id)` registers transmit messages. It registers
  **434 contiguous internal handles `0x100..0x1e9`** into a routing table
  (`DAT_00140442`) — a COM signal-handle space, not CAN ids (only ~24 ids are
  actually on the bus). The apparent `0x175 -> 0xFFFFBDD4` hit was a coincidental
  handle-number overlap, not a frame buffer.
- Because signal→PDU→frame assembly is **table-driven**, the byte-level mapping is
  in config tables, and the physical meaning of each signal lives in the software
  component that writes it — neither is practically recoverable by reading packing
  code.

This matches the DBC's own note that the telemetry frames are stubs. **The reliable
method is a correlated capture:** log the broadcast bus (0x175/179/180/181/321)
while the scanner reads known OBD/SDS values (RPM, TPS, coolant, speed), then match
bytes to values. One good drive log decodes them; firmware tracing does not.

RX frames are the exception and *are* decodable (the switch cluster 0x1D1 and cruise
0x321 were decoded from `FUN_7201A`/`FUN_72BB4`), because you read received bytes
directly rather than chase the COM transmit router.
