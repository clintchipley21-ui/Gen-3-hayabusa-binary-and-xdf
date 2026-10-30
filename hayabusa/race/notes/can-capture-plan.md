# CAN capture plan — Gen 3 Hayabusa

Goal: turn the raw cangaroo logs into a labelled signal map (DBC). We already have the
switch cluster (`0x1D1`) and the cruise state nailed down from the decompile + two traces.
What's missing is **ground truth**: which frame/byte moves when a *known* thing happens on the
bike. Each capture below isolates one thing so the changing bytes are obvious.

Load `hayabusa-gen3.dbc` (in this folder) into cangaroo first — every frame we've seen is already
named, so you'll be labelling against names instead of raw IDs.

---

## Rules that make decoding easy

1. **One thing at a time.** Do a single action, then hold still ~3–5 s before the next. The quiet
   gaps make the changing bytes jump out in a diff.
2. **Keep a timeline.** Note wall-clock (or stopwatch-from-capture-start) for each action. cangaroo
   timestamps are absolute, so `t≈12.3 s: SET tap` lets me line it up. A phone voice memo while you
   ride works great — I just need "what, and roughly when."
3. **Short files.** 20–60 s per run is plenty. One run per topic below, named for the topic, beats
   one giant log.
4. **Same bus settings every time.** Set cangaroo to the bike's powertrain-bus bitrate (almost
   certainly **500 kbps** — confirm once by checking that frames decode with no error frames) and
   **hex / absolute timestamps** (what the current logs use).
5. **Engine-off captures** (switches, throttle sweep) are safest to do first on the sidestand with
   the kill switch out; do the running ones (RPM, gear, mode, coolant) warmed up in a safe spot.

Send me the `.asc` plus your timeline notes and I'll fold the decodes into the DBC.

---

## Capture list (priority order)

### 1. Switch sweep — engine off, key on  *(fills `0x1D1` bytes 2/3/5, and any other switch frame)*
Press each control **on its own**, tap then 2.5 s hold where it applies, with a pause between:
- Cruise **SET** tap, then SET hold  *(known: byte4 0x08 / 0x0A — use these to verify your timeline sync)*
- Cruise **RES** tap, then RES hold  *(known: byte4 0x80 / 0xA0)*
- Cruise **ON/OFF** master switch (off→on→off)  *(this is what drives the real cruise flag)*
- **Mode / Select** button (the one that sets power mode A/B/C) — press through each mode
- Turn signals L / R / cancel, **horn**, **high/low beam**, **pass**, hazard if present
- **Start** button, **kill switch** off→on
- Anything else on the left/right pods

Why: maps every remaining switch bit, including `0x1D1` byte5 (a second active switch byte) and the
byte4 `0x40`/`0x04` bits we saw fire but can't yet name. These become free triggers for future features.

### 2. Power-mode change — engine running, stationary  *(critical for boost control)*
Warm, in neutral: cycle power mode **A → B → C → A**, pausing on each, and say which is active.
Why: the boost controller reads the active mode from a RAM pointer (**Mode Input Address**, default
`fef01f74`). Seeing which frame/byte changes with mode lets me **confirm that address is right** and
label the mode signal. This is the single most useful running capture.

### 3. RPM sweep — engine running, neutral
Blip to a few held RPMs you can read on the tach: ~1500, 3000, 5000, 7000. Call out each number.
Why: finds the RPM frame + scaling (expect a 16-bit big-endian value; tach ≈ raw·k).

### 4. Throttle sweep — engine off, key on
Roll the throttle slowly 0 → 100 → 0 %. (Engine off so it's just the TPS/grip signal, no revving.)
Why: finds the throttle-position frame and its 0–100 % scaling.

### 5. Gear sweep — on the stand or rolling slowly
Clutch in, shift **N → 1 → 2 → 3 → 4 → 5 → 6 → N**, pausing in each, calling out the gear.
Why: finds the gear-indicator signal (likely a small integer field).

### 6. Wheel speed — rolling (or spin the rear on the stand)
Accelerate to a couple of known speeds and hold; note the speedo reading. Front + rear if you can
(roll a bit on the stand spins only the rear → tells front vs rear apart).
Why: separates front/rear wheel-speed frames (ABS) and their km/h scaling.

### 7. Coolant warm-up — engine running from cold
Start cold, let it idle to fan-on, note dash temp at a few points (e.g. 40, 70, 95 °C).
Why: finds the ECT frame + scaling. Slow-moving, so even a rough timeline is fine.

### 8. Lean / IMU (if you want it) — engine off, rock the bike L/R
Tip side to side on the stand.
Why: `0x1A5` carries a signed value centred on `0x8000` that looks like lean/attitude — a lean
sweep confirms it.

### 9. Brake / clutch / neutral — engine off, key on
Squeeze front brake, press rear brake, pull clutch, in/out of neutral — each on its own.
Why: single-bit status signals, handy as extra gates/triggers later.

---

## Timeline note template (send this alongside each `.asc`)

```
capture: 02-powermode.asc   bus: 500k   date: ...
 t≈0     engine idling, mode A
 t≈6     -> mode B
 t≈12    -> mode C
 t≈18    -> mode A
 (end)
```

Rough seconds are fine — I align to the frames, I just need the order and the labels.
Captures 1 and 2 are the big wins; the rest fill in telemetry we can already read inside the ECU
but that's nice to have named on the bus.
