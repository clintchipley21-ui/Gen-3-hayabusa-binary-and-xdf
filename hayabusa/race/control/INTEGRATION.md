# Boost integration implementation and remaining ECU adapter

The portable controller, serialized calibration layout and optional BIN/XDF
preparation are implemented. **The controller is not linked into ECU firmware and
does not drive an output.** A prepared image is an offline integration artifact,
not a completed race BIN or an engine tune.

## Build the prepared BIN/XDF

From the repository root:

```sh
python3 hayabusa/tools/build_race_dev.py \
  hayabusa/stock/5JCZSJ40/5JCZSJ40.bin work/Race-integration-J40 \
  --sensor-preset gm-55567257-candidate --prepare-boost-integration
python3 -m unittest discover -s hayabusa/tools -p 'test_*.py' -v
```

Without `--prepare-boost-integration`, the previous baseline build is unchanged.
The prepared build requires the part-specific GM transfer. Other sensor curves
are rejected because the portable core currently implements this GM voltage
transfer, not an arbitrary sensor.

## TPS spare detachment and storage

Ghidra's V850E3V5 assembler produced the patch at `0x453B0`:

```text
66 e2  cmp 0x6,r28   ->   62 e2  cmp 0x2,r28
```

`FUN_4536C` retains the `cylinder * 6` descriptor stride and performs only the
first two TPS lookups per cylinder. `FUN_453B8` reads that first pair. This removes
the four spare lookups for each cylinder while retaining main/blend TPS results.
Neutral TPS lookups and the existing fault-selected alpha-N path are preserved.

One detached spare, cylinder 1 spare 1, is allocated: Z data `0x170440`, originally
26 columns × 50 rows × 16 bits (2600 bytes). Its descriptor `0x156478` has one
on-image pointer occurrence at `0x17EBEC` (slot 2 of the six-table family); Ghidra
reports its Z pointer at `0x156484` as the data reference. Preparation checks these
relationships and original instruction bytes before writing. The known exported
RAM consumers use only the first pair; this is static evidence, not hardware
validation or proof against every possible unidentified indirect access.

The first 576 bytes hold the profile; the remaining 2024 bytes and the original
TPS axes/descriptors remain unchanged. Only this one old table definition is
removed from the prepared XDF. Main TPS maps retain their original addresses,
data and fault behavior. Other detached spares are retained without allocation.

| Offset from `0x170440` | Layout |
|---|---|
| `0` | Eight-byte signature `RACEWG01` |
| `8`, `10` | Little-endian length 576 and version 1 |
| `12`, `13` | Controller enable (OFF), zero-based O2 channel (0 = channel 1) |
| `14`–`44` | 31-Hz frequency; duty bounds; pressure ceilings; PI gains; RPM/grip/ECT gates; voltage bounds; sample-age/tick limits |
| `64` | 16 little-endian RPM breakpoints, 0–15000 by 1000 |
| `96` | Seven little-endian gear labels, 0=N through 6 |
| `128` | Hat target, 7 gears × 16 RPM points, PSI × 100 |
| `352` | Base valve duty, same dimensions, basis points (0–10000) |

All targets/duties and PI gains ship zero. Enable is OFF and is deliberately not
exposed as an operational XDF switch while the runtime is absent. The two stored
tables and four exposed limits/gains are titled **RESERVED (runtime absent)**.
Editing these calibrations currently causes no boost-output behavior.

## Executable controller core

`race_control.c/.h` contains no ECU addresses or hardware writes. Its decoder reads
the actual serialized profile with explicit little-endian offsets; it does not
cast flash bytes to a compiler-dependent C struct. Core behavior includes:

- GM 55567257 candidate voltage-to-absolute-MAP conversion.
- HT-010910 matching-sensor voltage-to-PSI conversion, pending physical part identification.
- Per-gear RPM interpolation of hat target and base duty.
- PI pressure correction with bounded duty and integrator anti-windup.
- Disabled, stopped, neutral, low-RPM/grip/ECT, ALS and shift inhibition. ALS/shift
  inhibit boost duty by default; they do not replace the existing ALS/shifter code.
- Invalid configuration/sensors, stale samples, excessive tick gap, manifold
  overboost and excessive hat-pressure faults. Faults latch, zero requested duty
  and return an engine-cut request. Reset requires stopped and disarmed inputs.
- Unsigned timestamp wrap handling and the specified 31-Hz output frequency.

`test_race_control.c` runs against the profile bytes extracted from a real prepared
image. It is compiled natively with GCC warnings as errors and undefined-behavior
sanitization. These tests exercise control logic and serialization, not RH850
execution or physical pressure regulation. The native output is a test executable,
not a firmware blob. The code still needs an RH850 compiler/linker, ABI review and
source/blob verification before deployment.

This is a single-valve, hat-pressure PI core. It is not yet an outer manifold-boost
PID loop, dual fill/vent controller, adaptive feed-forward tune or full MAP-based
base ignition conversion. Base ignition in the inherited image remains TPS-based
with MAP retard. Fueling still uses the inherited normal SD path with TPS fault
fallback.

## O2 acquisition evidence

The extended headless export records:

```text
FUN_74EE4(0): logical acquisition channel 7 -> FEF02544
FUN_74EE4(1): logical acquisition channel 6 -> FEF02546
FUN_23354(channel): calls FUN_21B30(channel)
FUN_21B30: (buffer[channel] & 0x7fff) << 1
FUN_74EE4: result >> 6
FUN_75B18: copies FEF02544/46 to FEF0254C/4E
```

This establishes the software path and normalized range, not the relationship to
connector voltage, bias, protection or physical terminal. The core takes measured
millivolts and explicit valid/age information so it does not silently assume that
the O2 signal pin is electrically compatible with a 0.5–4.5-V transducer.

## Remaining physical/runtime adapter

The specified parts and selected channel are recorded in `../hardware-target.json`.
The remaining blockers are ECU electrical/pin/timer evidence and verification:

1. Establish O2 channel 1's physical signal terminal, reference/conditioning and
   permissible input range. Provide regulated 5-V sensor power separately from
   the heater's 12-V supply. Identify the delivered pressure-sensor marking.
2. Identify the actual heater driver command and all stock writers, physical
   terminal, current limit, polarity/flyback and PWM timer. The old heater-duty
   XDF curves do not establish this. Do not write guessed ports/request bits.
3. Replace stock channel ownership, closed-loop fuel feedback/learning, relevant
   diagnostics and heater scheduling coherently. Disabling a lamp or monitor
   alone does not release the output or remove fuel feedback.
4. Compile/link the core at verified free flash, allocate/init RAM, install a
   scheduler adapter, read coherent timestamped samples and call `race_tick`.
   Route fault engine-cut requests through a verified ECU cut path, and drive the
   actual PWM output at 31 Hz only when authorized. Output release must also work
   on missing task execution, reset and watchdog events.
5. Bench-verify that electrical OFF vents hat pressure with the actual pneumatic
   plumbing, and verify pressure conversion, frequency/duty, fault release and
   conflicts with PAIR air shift. Driver/timer behavior cannot be established by
   a native C test.

No physical driver binding or ECU controller hook is emitted until that evidence
exists. The build manifest explicitly reports `runtime_driver_installed: false`.
