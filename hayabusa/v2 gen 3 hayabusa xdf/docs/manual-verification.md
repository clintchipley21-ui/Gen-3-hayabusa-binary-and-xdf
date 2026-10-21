# Service-manual verification (sensor scalings + DTCs)

Source: **Suzuki Hayabusa Gen 3 Service Manual v1.0.0 (2022)**, 831 pp. (held in Dropbox
`/tuning stuff/hayabusa/Hayabusa Gen 3 Manual v1.0.0.pdf` — a Suzuki copyrighted document, **not
committed** to this repo, per the repo's manual-handling convention). Only derived facts are
recorded here and in `manual-dtc-names.csv`.

## 1. Sensor scalings — corroborated

Important: the ECU's **raw-count → engineering** formulas are derived from the *code* (axis
breakpoints in the decompile) and are the authoritative mapping. The manual gives physical sensor
specs and diagnostic voltages, which **corroborate** the code-derived scalings (sensor type, range,
polarity) without contradicting any of them.

| XDF conversion | Manual service data | Verdict |
|---|---|---|
| **RPM = raw / 2.56** | Idle speed **1050–1250 r/min**; fast idle 2100–2300 | ✓ consistent (idle maps decode to ~1150 rpm) |
| **TP / APS angle = raw / 364.08 deg** | TP sensor (main/sub) analog **0–5 V**; DTC trips `<0.20 V` / `>4.80 V` (P0120/P0123) | ✓ 0–5 V linear analog sensor, as the linear deg scaling assumes |
| **Pressure kPa = (raw − 7862) / 393.14** | IAP & AP sensors; P0069 checks AP-vs-IAP correlation with engine stopped (both read baro at rest) | ✓ IAP/AP are the two pressure sensors; offset form matches a baro-referenced sensor |
| **Temp °C = raw × 0.9375 − 30** (ECT, IAT) | NTC thermistors: ECT 20 °C = 2320–2590 Ω, 80 °C = 310–326 Ω; IAT 0 °C = 5400–6600 Ω, 80 °C = 290–390 Ω; fault `>4.90 V` / `<0.10 V` | ✓ NTC sensors linearised internally by the ECM; range consistent |
| **Battery V = raw / 51.2** | 12 V system, 12 V 11.2 Ah battery | ✓ |
| **Speed km/h = raw / 128** | Front + rear wheel-speed sensors; speed limiter / cruise present | ✓ sensors present; scaling is code-derived |
| Ignition deg = (raw − 64) × 0.3516 | — (no raw-count table in manual) | code-only; not contradicted |

Engine facts that sanity-check the fuel/ignition maps: 4-cylinder, 1340 cm³, bore 81.0 mm, stroke
65.0 mm, 12.5:1, throttle-body bore 43 mm, DENSO IU27D / NGK CR9EIA-9 plugs, PAIR solenoid 20–24 Ω,
HO2 heater 11.5–17.5 Ω.

**Conclusion:** no scaling needed changing. The manual confirms the sensor types, ranges and
polarities the code-derived conversions already use.

## 2. DTCs — our set validated and named

The DTC descriptor table decoded from the bin (`../../docs/dtc-table.csv`, **131 DTCs**) is a
**superset** of the manual's summary DTC Table (1A-13): every code the manual lists that the ECM
implements is present, and the bin additionally carries Suzuki-specific and later-section codes
(IAP P0105–P0107, catalyst P0420/P0430, ISC/idle P0505–P0522, EXCV P1400–P1406, Suzuki P16xx/P17xx,
ETV/APS P2101–P2135, etc.) that the manual documents in other sections or as LCD-only codes.

`manual-dtc-names.csv` holds the manual's **official SAE DTC names** (68 extracted) + the source
citation. These are used to enrich the DTC item titles/descriptions in the v2 XDFs (official name +
the manual's detecting condition where it adds a concrete threshold, e.g. TP `<0.20 V`/`>4.80 V`,
IAT/ECT `<0.10 V`/`>4.90 V`).
