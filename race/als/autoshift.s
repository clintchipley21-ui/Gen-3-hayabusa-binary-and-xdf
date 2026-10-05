# Auto-upshift (air-shifter) for Hayabusa Gen3 5JCZSJ40  (RH850 / v850e3v5)
# -----------------------------------------------------------------------------
# Fires the PAIR-valve output for a timed pulse when engine RPM reaches a per-gear
# target, to drive a relay -> MAC valve -> air ram that kicks the shift lever.
# No spark cut here: the factory quickshifter sees the lever load and cuts for the shift.
# Upshift only (gears 1->2 .. 5->6). Default OFF. All thresholds live in the CAL block
# and are exposed in the XDF.
#
# Runs once per cycle immediately AFTER the stock PAIR/EVAP output mapper FUN_5DB5E, by
# hooking its only call site (0x5DC9E: jarl 0x5DB5E -> jarl AUTOSHIFT_TICK). AUTOSHIFT_TICK
# calls FUN_5DB5E first, then has the last word on the output, so a forced pulse survives
# into the pin for that cycle.
#
# *** OUTPUT PRIMITIVE IS UNVERIFIED ON HARDWARE ***
# The exact PAIR drive bit and polarity are confirmed on the bench, not from static analysis.
# The only place the output is touched is the OUT_ON / OUT_OFF macros below (one spot). The
# XDF "Bench Test Output" switch holds OUT_ON steady so you can confirm which pin clicks, then
# the macro is finalised. Candidate: PAIR drive shadow fef020e0 bit2 + its enable fef020e1 bit0.

        .set AS_RAM,  0xfebfe008        # scratch RAM (ALS uses 0xfebfe000..+5)
        .set R_STATE, 0                 # u8  bit0 = locked out (shifted, waiting to re-arm)
        .set R_TIMER, 2                 # u16 pulse ticks remaining

        .set CAL,     0x000bf010        # auto-shift calibration block
        .set C_EN,    0                 # u8  0x80 = auto-upshift enabled
        .set C_TEST,  1                 # u8  0x80 = bench test: hold output asserted
        .set C_PULSE, 2                 # u16 output-on duration (task ticks)
        .set C_GRIP,  4                 # u16 min grip angle to allow a shift (WOT gate, X/364.08)
        .set C_REARM, 6                 # u16 rpm must fall this far below target to re-arm
        .set C_T1,    8                 # u16 1->2 target rpm (X/2.56)
        .set C_T2,    10                # u16 2->3
        .set C_T3,    12                # u16 3->4
        .set C_T4,    14                # u16 4->5
        .set C_T5,    16                # u16 5->6

        .set RPM,     0xfef0258c        # u16 engine rpm (X/2.56)
        .set GRIP,    0xfef025ec        # u16 grip/throttle request angle (X/364.08)
        .set GEAR,    0xfef026c2         # u8 gear bitmask: 1=N,2=1st,4=2nd,8=3rd,0x10=4th,0x20=5th,0x40=6th

        # ---- OUTPUT PRIMITIVE (the only code that touches the physical output) ----
        .macro OUT_ON
        mov     0xfef020e1, r16
        set1    0, 0[r16]               # PAIR subsystem enable (candidate)
        mov     0xfef020e0, r16
        set1    2, 0[r16]               # PAIR drive bit (candidate; flip to clr1 if bench shows inverted)
        .endm
        .macro OUT_OFF
        mov     0xfef020e0, r16
        clr1    2, 0[r16]
        .endm

        .section .as_code,"ax"
        .globl AUTOSHIFT_TICK

AUTOSHIFT_TICK:
        prepare {lp}, 0
        jarl    FUN_5DB5E, lp           # run the stock PAIR/EVAP output mapper first
        mov     AS_RAM, r10
        mov     CAL, r11
        # ---- bench test: hold the candidate output on, do nothing else
        ld.bu   C_TEST[r11], r12
        movea   0x80, r0, r13
        cmp     r13, r12
        bne     1f
        OUT_ON
        br      .Ldone
1:      # ---- enabled?
        ld.bu   C_EN[r11], r12
        cmp     r13, r12
        bne     .Ldone                  # disabled: leave the output to stock, return
        # ---- must be in a shiftable gear (1st..5th); else reset and output off
        mov     GEAR, r13
        ld.bu   0[r13], r12
        cmp     2, r12
        be      .Lgear
        cmp     4, r12
        be      .Lgear
        cmp     8, r12
        be      .Lgear
        movea   0x10, r0, r14
        cmp     r14, r12
        be      .Lgear
        movea   0x20, r0, r14
        cmp     r14, r12
        be      .Lgear
        # not a shiftable gear (neutral, 6th, invalid): disarm
        st.b    r0, 0[r10]              # clear state (lockout)
        st.h    r0, R_TIMER[r10]        # clear timer
        OUT_OFF
        br      .Ldone
.Lgear:
        # ---- pulse in progress?
        ld.hu   R_TIMER[r10], r15
        cmp     0, r15
        be      2f
        OUT_ON
        add     -1, r15
        st.h    r15, R_TIMER[r10]
        cmp     0, r15
        bne     .Ldone                  # still pulsing
        OUT_OFF                         # pulse just ended: latch lockout until re-arm
        set1    0, 0[r10]
        br      .Ldone
2:      # ---- not pulsing: pick this gear's target into r14
        cmp     2, r12
        bne     3f
        ld.hu   C_T1[r11], r14
        br      .Lhavetgt
3:      cmp     4, r12
        bne     4f
        ld.hu   C_T2[r11], r14
        br      .Lhavetgt
4:      cmp     8, r12
        bne     5f
        ld.hu   C_T3[r11], r14
        br      .Lhavetgt
5:      movea   0x10, r0, r13
        cmp     r13, r12
        bne     6f
        ld.hu   C_T4[r11], r14
        br      .Lhavetgt
6:      ld.hu   C_T5[r11], r14          # must be 5th (0x20) by elimination
.Lhavetgt:
        mov     RPM, r13
        ld.hu   0[r13], r15             # r15 = rpm
        # ---- locked out? clear only once rpm has fallen target-REARM below target
        tst1    0, 0[r10]
        bz      .Larmed
        ld.hu   C_REARM[r11], r13
        mov     r14, r12
        sub     r13, r12                # r12 = target - REARM
        cmp     r12, r15
        bnl     .Ldone                  # rpm still high: stay locked
        clr1    0, 0[r10]               # re-armed
        br      .Ldone
.Larmed:
        # ---- WOT gate: grip >= min
        mov     GRIP, r13
        ld.hu   0[r13], r13
        ld.hu   C_GRIP[r11], r12
        cmp     r12, r13
        bl      .Ldone                  # not WOT: do not shift
        # ---- rpm >= target?
        cmp     r14, r15
        bl      .Ldone                  # below target: wait
        # ---- fire: start the output pulse
        ld.hu   C_PULSE[r11], r15
        st.h    r15, R_TIMER[r10]
        OUT_ON
.Ldone:
        dispose 0, {lp}, [lp]
