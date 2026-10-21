# Electrical ratings research — 2026-10-21

These are published operating specifications and explicitly identified supplier
cross-references. They do not change firmware enable states or establish wiring
compatibility. No new runtime adapter has been installed.

| Device | Located specifications | Evidence level / unresolved ratings |
| --- | --- | --- |
| GM 55567257 / ACDelco 213-4760 MAP | Nominal 5-V supply. Supplier cross-reference pin numbering: 1 supply, 2 ground, 3 signal. DSX normalized span 312.5 kPa and offset -11.25 kPa. | GM confirms part identity; voltage/pinout from NZEFI Bosch/GM cross-reference. Exact supply tolerance, current consumption and absolute maximum not located. |
| Hat sensor, likely Haltech HT-010910 | Nominal 5-V supply. 0.5 V at 0 PSI gauge; 4.5 V at 150 PSI gauge. Haltech harness-side drawing: A signal ground, B +5 V, C signal. | Haltech manufacturer info sheet, revision 4.1, visually checked. Seller metadata identifies brand Haltech but has a blank SKU; delivered marking still unconfirmed. Supply tolerance/current not specified in located sheet. |
| AEM 30-2400 | 12 VDC, 31 Hz, 10–90% operating duty. Coil polarity unimportant per AEM manual. Normally one wire switched 12 V, other driver output. | Manufacturer confirmed. Manual does not specify coil resistance, current, inductance or suppression/clamp requirements. |
| Candidate MAC 35A-AAA-DDBA-1BA equivalent | Retailers report 5.4 W, measured 25.4 ohms, approximately 0.45 A at 12 V. | Separate MAC part: replacement equivalence to AEM is a retailer claim, not manufacturer confirmation. Do not transfer ratings to the AEM valve as established facts. |
| Stock O2 heater | 11.5–17.5 ohms at 23 C. | Suzuki service manual 1C-9. Approximately 0.69–1.04 A at 12 V is calculated from this resistance, not a driver rating or hot operating-current specification. |
| Stock PAIR coil | 20–24 ohms at 20–30 C. | Suzuki service manual maintenance section. Approximately 0.50–0.60 A at 12 V, calculated; not an airshift replacement-solenoid rating. |
| ECU O2 input / heater driver | O2 normally about 0–1 V. Manual identifies signal A/T24, return A/T28, heater C/T79; PAIR C/T94. | Absolute maximum input voltage, input impedance/transfer, heater output current rating, inductive clamp energy and usable PWM hardware remain unpublished in located sources. |

## GM range and calibration

At nominal 5-V supply, interpreting DSX's normalized calibration gives
`P_absolute_kPa = 62.5 * Vsignal - 11.25`. Thus 0.5 V corresponds to 20 kPa,
4.5 V to 270 kPa and 4.75 V to 285.625 kPa. These are calculations from the
supplier's calibration, not independently measured sensor endpoints.

NZEFI identifies its Bosch cross-referenced part as 2.7 bar and explicitly warns
that it is often sold as 3 bar. Facet's replacement datasheet for OE 55567257 lists
10–286 kPa and 332.1–4750 mV, consistent with approximately this slope. That
replacement is not proof of the genuine sensor's absolute maximum ratings.
Retain the prepared profile's 270-kPa absolute ceiling pending calibration checks;
300-kPa tables should not be justified by the sales name alone.

The HT-010910 calibration is gauge pressure, unlike manifold absolute pressure.
The software already keeps those units separate. Pins A and B must follow the
manufacturer drawing: **A ground, B +5 V**. Do not substitute heater battery power
for regulated sensor power.

## What the load comparison establishes

A 25.4-ohm candidate coil would draw about 0.47 A at 12 V and 0.57 A at 14.4 V
using constant resistance, below the stock heater's calculated current at the same
voltage and stated room-temperature resistance. This makes the proposed output
worth investigating. It does not establish the AEM coil's actual resistance,
transient current, heater driver's inductive-load compatibility or 31-Hz operation.
A heater is chiefly resistive; a solenoid stores energy and creates a turn-off
transient. No flyback diode, resistor or direct connection is specified here based
on an unverified driver circuit. Supplier listings with internally inconsistent
resistance/current values were not used as electrical specifications.

ECU blank replacement part is Suzuki **32910-10L00**. The 2022 fiche lists O2
parts **18213-04K00** and **18213-18K00**, and PAIR air-cut valve **18510-29G31**.
The fiche alone does not bind the two O2 part numbers to firmware channel numbers.
No public datasheet located for the complete ECU gives the missing pin ratings.
Those require ECU-internal component identification/schematic evidence or controlled
bench characterization, rather than inferring limits from a sensor part number.

## Sources

- [GM identity / ACDelco cross-reference](https://parts.chevrolet.com/product/gm-genuine-parts-manifold-absolute-pressure-%28map%29-sensor-%28programming-required%29-55567257)
- [NZEFI sensor supply, numbered pinout and 2.7-bar explanation](https://www.nzefi.com/product/gm-2-7-bar-map-sensor-ls9-lsa/)
- [DSX calibration](https://dsxtuning.com/products/gm-3-bar-map-55567257)
- [Facet replacement data](https://www.facet.it/site/assets/files/1286/fa-sen19q2-lr-pf.pdf)
- [Haltech HT-010910 manufacturer sheet](https://store.haltech.com/wp-admin/admin-ajax.php?action=ht_get_file&id=5d30ec73506c256cc772dc06&op=1)
- [AEM manufacturer manual, 30-2400](https://documents.holley.com/fe590cc4b242b6e955e9d12f206ba0e0cc7dd5c7.pdf)
- [MAC candidate load specifications, retailer](https://ecrperformance.com/mac-valve-boost-controller-kit/)
- [MAC/AEM replacement claim, retailer](https://paradiseracing.com/products/mac-boost-control-solenoid-35a-aaa-ddba-1ba)
- [Suzuki GSX1300RM2 service manual](https://www.scribd.com/document/1056621071/2020-2022-GSX1300RR-99500-10L00-01E-GSX1300RM2-unlocked)
- [Suzuki 2022 parts catalogue](https://www1.suzuki.co.jp/motor/support/parts_catalog_manage/files/GSX1300RRQM2.pdf)
- [2022 O2 parts fiche](https://www.revzilla.com/oem/suzuki/2022-suzuki-hayabusa/muffler?submodel=gsx1300rrqm2)
- [2022 PAIR parts fiche](https://www.revzilla.com/oem/suzuki/2022-suzuki-hayabusa/2nd-air?submodel=gsx1300rrqm2)
