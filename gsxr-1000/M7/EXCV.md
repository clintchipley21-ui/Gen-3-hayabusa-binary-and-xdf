# GSX-R1000 M7 — EXCV (Exhaust Control Valve) quick reference

The EXCV items needed to **control the valve** and **control its DTCs** live in
each of the four M7 XDFs (`32990-48L00/10-US/20-EU/30.xdf`) under two folders:
**"Exhaust Control Valve (EXCV) - Valve Control"** and
**"Exhaust Control Valve (EXCV) - DTC Control"**. Load the XDF for your bin in
CalStudio and open those two folders. Addresses are identical across all four
bins (base traced on `32990-48L00`). This file is the quick reference for them.

All addresses and stock values are **code-proven** from the binary (Ghidra V850
decompile, state-machine `FUN_0007899C` family). The EXCV is a cable-driven servo
with a position-feedback pot on ADC channel `0x33`, driven bang-bang (discrete
setpoints) through an H-bridge. **Unverified on hardware** — change setpoints in
small steps and watch for P1404.

## Live signals (RAM — read-only, not in the XDF)

These are runtime values, not calibration. Use them for datalogging / scanning,
not editing.

| Signal | RAM addr | Notes |
|---|---|---|
| Valve demand (target) | `0xFEBF62BE` | what the state machine commands |
| Drive duty | `0xFEBF62CC` | commanded motor duty |
| Position feedback | `0xFEF025DA` | pot via ADC ch `0x33`, raw 0–1023 |
| PWM output (lo/hi) | `0xFEBF603D` / `0xFEBF603E` | H-bridge drive |

## Valve control (category "EXCV - Valve Control")

| Item | Addr | Size | Stock | Meaning |
|---|---|---|---|---|
| Motor voltage-comp map A | `0x16638C` | 9×23 u8 | ~0x80 | duty × battery-V comp (x-brk `0x1587AC`, y-brk `0x1587DC`) |
| Motor voltage-comp map B | `0x16645C` | 9×23 u8 | ~0x80 | duty × battery-V comp (x-brk `0x1587F0`, y-brk `0x158820`) |
| Target — near-full open | `0x172E96` | u16 | 1020 | ~full-open demand setpoint |
| Open/close decision thr. | `0x172E98` | u16 | 553 | state-machine open↔closed switch |
| Engage gate (speed/RPM) | `0x172E9A` | u16 | 463 | condition that enables motion |
| Target — CLOSED | `0x172E9C` | u16 | 204 | closed-position setpoint (raw 0–1023) |
| Target — OPEN | `0x172E9E` | u16 | 828 | open-position setpoint (raw 0–1023) |
| Active-drive time limit | `0x172F3A` | u16 | 1328 | max drive duration |
| Direction hysteresis A | `0x172F3B` | u8 | 5 | |
| Direction hysteresis B | `0x172F3C` | u8 | 5 | |
| Direction hysteresis C | `0x172F3D` | u8 | 1 | |
| Direction hysteresis D | `0x172F3E` | u8 | 26 | |
| Drive clamp / limit | `0x172F48` | u8 | 255 | |
| **Master enable** (flag) | `0x172F32` | mask `0x80` | on | `0x80`=EXCV control active |
| **Output arm** (flag) | `0x167105` | mask `0x80` | on | `0x80`=motor output armed |

To **force the valve fully open** (common exhaust mod): raise the CLOSED setpoint
(`0x172E9C`) toward the OPEN value, or leave the mechanism open and disable the
DTCs below so no P1404 sets. Do not simply clear Master enable unless you also
suppress the DTCs — a disabled servo with the position sensor live can trip P1404.

## DTC control (category "EXCV - DTC Control")

Six **MIL-enable flags**, mask `0x01` on the DTC record's lamp byte (clear the bit
to stop that code lighting the MIL / logging). Plus the position-sensor monitor
thresholds the state machine compares against.

| DTC / item | Addr | Type | Stock | Meaning |
|---|---|---|---|---|
| P1400 MIL enable | `0x1A1DE4` | flag `0x01` | on | pos-sensor LOW (short-to-gnd) |
| P1402 MIL enable | `0x1A1DCC` | flag `0x01` | on | pos-sensor HIGH (open/short-to-pwr) |
| P1404 MIL enable #1 | `0x1A1DFC` | flag `0x01` | on | valve range / stuck |
| P1404 MIL enable #2 | `0x1A1E14` | flag `0x01` | on | valve motion / stall |
| P1404 MIL enable #3 | `0x1A2174` | flag `0x01` | on | valve fault (master warning) |
| P1404 MIL enable #4 | `0x1A218C` | flag `0x01` | on | valve fault |
| P1400 LOW threshold | `0x15597E` | u16 | 29 | pos-sensor low trip |
| P1402 HIGH threshold | `0x155980` | u16 | 1004 | pos-sensor high trip |
| P1404 range low-normal | `0x1559A6` | u16 | 49 | range window |
| P1404 range high-normal | `0x1559A8` | u16 | 983 | range window |
| P1404 range low-limit | `0x1559AA` | u16 | 29 | range window |
| P1404 range high-limit | `0x1559AC` | u16 | 1004 | range window |
| P1404 stall time limit | `0x155B1C` | u16 | 125 | motion timeout |

**To delete the EXCV codes** after removing/fixing the valve: clear the `0x01`
bit on the six MIL-enable flags. Widening the P1404 range window
(`0x1559A6…0x1559AC`) and the stall limit (`0x155B1C`) instead keeps the monitor
but tolerates a modified mechanism.

---
_DTC record format: GSX-R uses 24-byte records (table base `0x1A18EC`); lamp @ +0
(bit0 = MIL-enable), SAE code lo @ +9 / hi @ +10, RAM status @ +20. Full trace in
`gsxr-1000/docs/tracing.md` §3v._
