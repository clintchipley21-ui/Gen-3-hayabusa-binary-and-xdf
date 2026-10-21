# Boost control (wastegate solenoid PWM) for Hayabusa Gen3 5JCZSJ40  (RH850 / v850e3v5)
# -----------------------------------------------------------------------------
# Software-PWMs a RACE-UNUSED output to a boost-control / wastegate solenoid (a MAC-style
# duty valve bleeding wastegate dome / actuator pressure). Duty is scheduled PER GEAR so you
# can run less boost in the low gears and more up top. An optional closed-loop trim nudges the
# duty toward a target manifold pressure read from a sensor on a repurposed O2 SIGNAL input.
#
# WHY THE O2 CIRCUIT: on a turbo build the stock narrowband O2 sensors are useless (and usually
# deleted), so BOTH halves of an O2 circuit are free: its low-side HEATER driver becomes the
# solenoid output, and its SIGNAL input becomes a 0-5 V boost-pressure input. You give up stock
# closed-loop fuel trim on that bank, which a speed-density race tune does not use anyway.
#
# Runs once per output-mapper cycle (~5 ms) by hooking the second call in FUN_5dc9a
# (0x5dca2: jarl 0x5dc64 -> jarl BOOST_TICK). BOOST_TICK calls FUN_5dc64 first, then has the
# last word on the output that cycle (same technique the air-shifter uses for the PAIR output).
# Upshift/air-shift uses the PAIR output; boost uses the O2-heater output; they do not collide.
#
# *** OUTPUT AND INPUT PRIMITIVES ARE UNVERIFIED ON HARDWARE ***
# The exact O2-heater drive bit/polarity and the O2-signal ADC word are confirmed on the bench,
# not from static analysis. Every hardware touch is isolated to the OUT_ON / OUT_OFF macros and
# the PRESS_IN address below (one spot each). The XDF "Bench Test Output" switch holds the
# solenoid asserted so you can confirm which pin drives it; closed loop ships OFF so the
# (also unverified) pressure input is never on the critical path until you have proven it.
# Ships DISABLED. Default per-gear duties are all 0 = wastegate spring pressure (lowest boost).

        .set B_RAM,   0xfebfe010        # scratch RAM (ALS 0xfebfe000..5, air-shift 0xfebfe008..a)
        .set R_PHASE, 0                 # u16 software-PWM phase counter (0..period-1)
        .set R_TRIM,  2                 # s16 closed-loop duty trim (added to the gear duty)

        .set CAL,     0x000bf030        # boost calibration block (see apply_patches.py BOOST_CAL)
        .set C_EN,    0                 # u8  0x80 = boost control enabled
        .set C_TEST,  1                 # u8  0x80 = bench test: hold the solenoid output asserted
        .set C_CL,    2                 # u8  0x80 = closed-loop trim enabled (needs PRESS_IN proven)
        .set C_PER,   4                 # u16 PWM period in task ticks (duty is 0..period)
        .set C_MINR,  6                 # u16 min rpm to run the solenoid (X/2.56); below -> off
        .set C_D1,    8                 # u16 duty gear 1  (ticks on per period)
        .set C_D2,    10                # u16 duty gear 2
        .set C_D3,    12                # u16 duty gear 3
        .set C_D4,    14                # u16 duty gear 4
        .set C_D5,    16                # u16 duty gear 5
        .set C_D6,    18                # u16 duty gear 6
        .set C_TGT,   20                # u16 closed-loop target (PRESS_IN raw ADC counts)
        .set C_STEP,  22                # u16 closed-loop trim step (duty ticks per period)

        .set RPM,     0xfef0258c        # u16 engine rpm (X/2.56)      [confirmed, shared with air-shift]
        .set GEAR,    0xfef026c2         # u8 gear bitmask 1=N,2..0x40=6th [confirmed, shared with air-shift]
        .set PRESS_IN,0xfef02648        # u16 boost-pressure ADC on the repurposed O2 signal input
                                        #     *** CANDIDATE - confirm the O2-signal ADC word on the bench ***

        # ---- OUTPUT PRIMITIVE (the only code that touches the physical solenoid output) ----
        # Candidate: O2-heater drive shadow fef020e4 bit0 (extra output-shadow block fef020e2..e6).
        # Flip set1<->clr1 if the bench shows the drive inverted; move the address/bit if the bench
        # shows a different pin. This is a two-line change, then re-run build.sh and re-apply.
        .macro OUT_ON
        mov     0xfef020e4, r16
        set1    0, 0[r16]
        .endm
        .macro OUT_OFF
        mov     0xfef020e4, r16
        clr1    0, 0[r16]
        .endm

        .section .boost_code,"ax"
        .globl BOOST_TICK

BOOST_TICK:
        prepare {lp}, 0
        jarl    FUN_5DC64, lp           # run the stock routine this call site displaced
        mov     B_RAM, r10
        mov     CAL, r11
        # ---- bench test: hold the solenoid on, do nothing else
        ld.bu   C_TEST[r11], r12
        movea   0x80, r0, r13
        cmp     r13, r12
        bne     1f
        OUT_ON
        br      .Ldone
1:      # ---- enabled?  (disabled -> solenoid off = wastegate spring pressure, reset phase)
        ld.bu   C_EN[r11], r12
        cmp     r13, r12
        be      2f
        st.h    r0, R_PHASE[r10]
        st.h    r0, R_TRIM[r10]
        OUT_OFF
        br      .Ldone
2:      # ---- min-rpm gate: rpm < C_MINR -> off, hold phase/trim reset (no boost off-throttle/idle)
        mov     RPM, r13
        ld.hu   0[r13], r15             # r15 = rpm
        ld.hu   C_MINR[r11], r12
        cmp     r12, r15
        bnl     3f                      # rpm >= min: run
        st.h    r0, R_PHASE[r10]
        st.h    r0, R_TRIM[r10]
        OUT_OFF
        br      .Ldone
3:      # ---- pick this gear's duty into r14 (neutral / unknown -> 0 = off)
        mov     GEAR, r13
        ld.bu   0[r13], r12
        mov     0, r14
        cmp     2, r12
        bne     31f
        ld.hu   C_D1[r11], r14
        br      .Lhavetgt
31:     cmp     4, r12
        bne     32f
        ld.hu   C_D2[r11], r14
        br      .Lhavetgt
32:     cmp     8, r12
        bne     33f
        ld.hu   C_D3[r11], r14
        br      .Lhavetgt
33:     movea   0x10, r0, r13
        cmp     r13, r12
        bne     34f
        ld.hu   C_D4[r11], r14
        br      .Lhavetgt
34:     movea   0x20, r0, r13
        cmp     r13, r12
        bne     35f
        ld.hu   C_D5[r11], r14
        br      .Lhavetgt
35:     movea   0x40, r0, r13
        cmp     r13, r12
        bne     .Lhavetgt               # neutral / invalid: r14 stays 0 (off)
        ld.hu   C_D6[r11], r14
.Lhavetgt:
        # ---- optional closed-loop trim: effective duty = gear duty + trim, trim stepped toward target
        ld.bu   C_CL[r11], r12
        movea   0x80, r0, r13
        cmp     r13, r12
        bne     .Lnoloop
        # measured pressure vs target
        mov     PRESS_IN, r13
        ld.hu   0[r13], r12             # r12 = measured raw ADC
        ld.hu   C_TGT[r11], r13         # r13 = target raw ADC
        ld.hu   R_TRIM[r10], r17        # r17 = current trim (treated signed)
        ld.hu   C_STEP[r11], r18        # r18 = step
        cmp     r13, r12
        bl      .Lunder                 # measured < target: need more boost -> trim up
        sub     r18, r17                # measured >= target: back off
        br      .Lclamptrim
.Lunder:
        add     r18, r17                # trim up
.Lclamptrim:
        # clamp trim to +/- period so it cannot run away
        ld.hu   C_PER[r11], r19
        cmp     r19, r17
        ble     36f
        mov     r19, r17
36:     mov     r19, r20
        subr    r0, r20                 # r20 = -period
        cmp     r20, r17
        bge     37f
        mov     r20, r17
37:     st.h    r17, R_TRIM[r10]
        add     r17, r14                # effective duty = gear duty + trim
.Lnoloop:
        # ---- clamp effective duty to [0, period]
        cmp     0, r14
        bge     38f
        mov     0, r14
38:     ld.hu   C_PER[r11], r19
        cmp     r19, r14
        ble     39f
        mov     r19, r14
39:     # ---- software PWM: ON while phase < duty, advance phase, wrap at period
        ld.hu   R_PHASE[r10], r15
        cmp     r14, r15
        bl      .Lon                    # phase < duty -> output on
        OUT_OFF
        br      .Ladv
.Lon:
        OUT_ON
.Ladv:
        add     1, r15
        ld.hu   C_PER[r11], r19
        cmp     r19, r15
        bl      .Lstore                 # phase < period: keep
        mov     0, r15                  # wrap
.Lstore:
        st.h    r15, R_PHASE[r10]
.Ldone:
        dispose 0, {lp}, [lp]
