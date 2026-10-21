# Combined race development build

This is a development foundation for the requested race firmware, **not the completed
race package and not validated for flashing**. The source repository itself labels
all custom firmware unverified on hardware.

The new builder composes the existing speed-density v3 changes, rolling anti-lag
v4.1 and assembled air-shifter into a variant-preserving image, matching XDF and
machine-readable change manifest. ALS, auto-shift and bench-output override ship OFF.
The original race files and the stock binaries are not changed.

## Build and inspect

From the repository root:

```sh
python3 hayabusa/tools/build_race_dev.py \
  hayabusa/stock/5JCZSJ40/5JCZSJ40.bin work/Race-dev-J40
python3 -m unittest discover -s hayabusa/tools -p test_race_dev.py -v
```

This produces `.bin`, `.xdf` and `.json` under the requested prefix. Existing output
paths and input/output collisions are rejected. Known reference payloads and input
stock images are SHA-256 checked before any output is written. Modified images,
short reads and unknown variants are rejected. Field-1 CRC is stamped automatically;
field 3 is preserved and its enforcement is unresolved.

Supported exact stock reads: J00, J10, J20, J30, J40, JA0 and NC0. **JB0 is not
supported by this SD port:** 16,446 bytes that the J40 SD patch changes already
differ in JB0. Copying the J40 fuel calibration into JB0 without a separate port
would silently replace variant calibration. The original ALS/air-shift-only tool
remains available for stock reads.

## Sensor calibration: 3 bar or 2.5 bar

The specified hardware target is **GM 55567257**, original IAP input, PAIR for
air shift, and an O2 connector for wastegate-hat sensing and PWM. Those assignments
are recorded in [hardware-target.json](hardware-target.json), with unresolved
electrical/channel details left explicit.

Use this part-specific **candidate** development preset:

```sh
python3 hayabusa/tools/build_race_dev.py \
  hayabusa/stock/5JCZSJ40/5JCZSJ40.bin work/Race-dev-J40-GM55567257 \
  --sensor-preset gm-55567257-candidate
```

[GM's listing](https://parts.chevrolet.com/product/gm-genuine-parts-manifold-absolute-pressure-%28map%29-sensor-%28programming-required%29-55567257)
identifies 55567257 as ACDelco 213-4760.
[DSX's part-specific published calibration](https://dsxtuning.com/products/gm-3-bar-map-55567257)
gives a 312.50-kPa normalized span and -11.25-kPa offset. Interpreting the normalized
span over the 5-V supply gives `P = 62.5 * V - 11.25`, or
`P = raw * (312.5/1023) - 11.25` for the assumed ratiometric 10-bit ADC. This is
an implementation assumption from supplier tuning data, not an OEM electrical
datasheet or a measured transfer on this ECU. The preset uses 20–270 kPa table
axes (approximately 0.5–4.5 V), avoiding the near-rail 300-kPa endpoint by default.
`--max-kpa` can override the table ceiling, subject to representation/fault checks;
this does not establish accuracy beyond a validated sensor range.

The default **without** a preset retains the historical image for reproducibility:

The default build retains the project's **provisional** 3-bar transfer:

`pressure_kPa_absolute = raw_ADC * 0.307429 - 12.6`

This is not verified against a particular GM sensor. A nominal pressure range is
insufficient to choose a transfer curve. The default image is for offline review
until the exact part or measured transfer is known.

For a measured or datasheet curve `P = a * raw_ADC + b`, supply all three options:

```text
--sensor-slope a --sensor-offset b --max-kpa ceiling
```

For a voltage-domain curve `P = m * V + b`, convert using the actual ADC reference
and full-scale code: `a = m * Vref / ADC_full_scale`. Do not substitute kPa/V into
the ADC-slope option. Verify the ADC/reference assumption on the ECU. Supply absolute
pressure, not gauge pressure.

For a 2.5-bar-range sensor, choose a ceiling at or below 250 kPa absolute and within
its measured electrical range and fault thresholds. The builder rejects axes that
reach the circuit-fault thresholds. No guessed GM 2.5-bar preset is included.

All eight SD fuel tables and both MAP retard tables are re-axised together. Z rows
are linearly resampled at the new physical pressures; the old 300-kPa fuel cell is
not merely relabeled as 250 kPa. The non-uniform pressure spacing is preserved in
proportion to the new range. Sensor gain/offset and XDF equations change together:

`gain = round(393.14 * a * 10925 / 32)`

`offset_word = round(32768 + 393.14 * b)`

The barometric sensor and stock internal pressure scale remain unchanged. The
stock-side IAP representation still saturates near 147 kPa; SD/retard maps use raw
IAP ADC. Raw ADC filtering, injector scaling, actual AFR and ignition need validation.
Resampled values are starting calibration, not an engine tune.

## Why the TPS fuel storage has not been repurposed

Static evidence from the supplied Ghidra project/export:

| Function | Evidence and consequence |
|---|---|
| `0x4536C` | Reads six TPS table descriptors per cylinder via the pointer family at `0x17EBE4`; all six lookups still execute. |
| `0x453B8` | Blends the first TPS pair into the TPS fuel result. A zero within-family blend does not disable the entire TPS path. |
| `0x454DA` | Reads the neutral/clutch TPS table family at `0x154D8C`. |
| `0x4558A` / `0x455B8` | Call both IAP and TPS lookup routines. |
| `0x491BC` | Sets final TPS/IAP selector `0xFEF011CA` to `0x100` on fault branches. |
| `0x45E92` | Uses `0xFEF011CA` in the final fuel quantity calculation. |

The 28 TPS fuel definitions are labeled **TPS STORAGE - NOT RELEASED** in the new
XDF; their addresses and bytes remain intact. Original spare/blend labels are
retained so calculated-but-unselected maps are distinguishable from the main maps.
An unconditional table reader is still a consumer even if its result currently has
zero selection weight. This audit is not a claim that every spare contributes fuel.

To reclaim this area, implement and verify the replacement readers, explicitly
resolve the fault path and its effect on fuel/boost, then establish a no-reader
invariant for the allocated bytes. Only then rename those specific slots as boost
target/base duty/limits. Renaming an XDF table does not install that behavior.

## Ignition and boost control still to implement

The inherited ignition changes are **MAP-based retard on top of TPS-based base
advance**, not full speed-density base ignition. The retard participates in a
maximum-of-retards selection, not an additive stack, and does not cover every
idle/neutral timing path. A complete SD ignition conversion needs a trace of base
advance selection and those paths, appropriate MAP axes and actual calibration.

The existing air-shift source writes `0xFEF020E0` bit 2 and `0xFEF020E1` bit 0, but
its own notes mark those bits and polarity unverified. The code at `0x5DB5E`
consumes `0xFEF020E0` as **state transition requests**, so treating it as a proven
physical output/PWM register is not justified. Setting another request bit does
not establish an independent EVAP boost solenoid output.

No boost solenoid driver, target/duty maps masquerading as connected controls, or
guessed port writes are installed. Completing it requires:

1. Identify an electrically suitable unused terminal, its driver, flyback/load
   limits and polarity, separate from the air-shifter's output.
2. Trace the complete command-to-pin path, its writers, startup/reset state and
   diagnostic ownership. Establish the available PWM timer and frequency.
3. Implement output arbitration, enable conditions, bounded duty, MAP plausibility,
   overboost handling and fault/disarm behavior with a known wastegate plumbing state.
4. Integrate the controller, schedule/timer and calibration storage; assemble actual
   RH850 instructions and verify calling convention, branch ranges and source/blob match.
5. Bench-confirm the selected terminal, PWM frequency/duty, output release and
   fault/reset behavior before an engine/boost test.

For the O2 proposal, the sensor signal and heater output are separate circuits.
The O2 signal's permitted voltage range, bias and conditioning must be established
before connecting a pressure transducer; software rescaling cannot change that
input circuit. The heater driver needs a separate pin/timer/load/flyback audit
before driving a pneumatic valve. Channel 1 is selected under the user's permission
to choose either O2 channel. The GM sensor replacing the original IAP is confirmed.

The chosen [Tuner Tools 150-PSI Motorsport sensor](https://tunertools.com/products/150-psi-motorsport-fuel-oil-wastegate-pressure-sensor)
has the same description as Haltech HT-010910; the seller's product JSON does not
provide a manufacturer SKU, so confirm the physical marking before using that
calibration. [Haltech's HT-010910 information sheet](https://store.haltech.com/wp-admin/admin-ajax.php?action=ht_get_file&id=5d30ec73506c256cc772dc06&op=1)
specifies 0 PSI at 0.5 V and 150 PSI at 4.5 V: `PSI = 37.5 * V - 18.75`.
It needs regulated 5-V sensor power, not the heater's 12-V supply. Input conditioning
and the pressure reference must be confirmed for hat-pressure feedback.

The chosen actuator is **AEM 30-2400**. Its [manufacturer instructions](https://documents.holley.com/fe590cc4b242b6e955e9d12f206ba0e0cc7dd5c7.pdf)
specify 12-V operation, 31 Hz, an operating duty range of 10–90% and 120-PSI maximum
pressure. Energized flow joins ports 1–2; deenergized flow joins ports 2–3.
The hat plumbing must make the disarmed state release pressure; an output-off bit
alone does not establish that pneumatic state. The 150-PSI sensor range is not a
permitted 150-PSI operating limit for the 120-PSI valve. Coil current, driver
capacity, flyback and the actual ECU terminal/timer remain unresolved.

The existing XDF's two "HO2 Heater Duty" curves (`0x1544D4`, `0x154500`) are not
verified heater-output duty controls. Readers `0x3DBAE`, `0x3DDB2` and `0x3E036`
compare sums of HO2 correction state (`0xFEF0118C/E` and `0xFEF011DA/DC`).
`0x44996` updates the former through the HO2 feedback history, and `0x484E0`
sets the latter. The new XDF labels these correction/diagnostic limits with an
unverified driver role; the binary values remain unchanged. Do not base a wastegate
output patch on the old labels.

A bench test cannot be replaced by static disassembly.

## Re-run the Ghidra audit

The included [headless export](audit/ghidra-j40-race-audit.txt) was generated with
Ghidra 12.1.4 and Temurin JDK 25 against the repository's existing analysis project,
with `-noanalysis -readOnly`. It records `V850:LE:32:v850e3v5` and executable SHA-256
`676daf1c0048e9d0622b4ab2466f3e98e22e29623185d1c602698700f63c0c8d`, matching
the shipped stock J40 read. All requested functions decompiled. This reuses the
supplied analysis; it is not a new whole-image auto-analysis or an ECU emulator run.

`tools/ghidra/RaceAudit.java` exports instructions, decompilation and references for
the relevant dependencies. Extract `re/ghidra.zip` to an intermediate directory,
use a compatible Ghidra version, and run against a **copy** of the project:

```sh
analyzeHeadless work/gproj busa -process -noanalysis -readOnly \
  -scriptPath hayabusa/tools/ghidra \
  -postScript RaceAudit.java /absolute/path/to/work/ghidra-race-audit.txt
```

The archived project records its owner as `root`. Set the OWNER in the copied
`busa.rep/project.prp` to the current local user if Ghidra refuses to open it.
The source archive remains untouched. Keep the exported program SHA-256 with the
audit so the analyzed image is identifiable.
