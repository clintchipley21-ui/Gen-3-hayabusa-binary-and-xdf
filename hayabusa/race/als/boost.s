# Boost control (wastegate solenoid PWM) for Hayabusa Gen3 5JCZSJ40  (RH850 / v850e3v5)
# -----------------------------------------------------------------------------
# Software-PWMs a RACE-UNUSED output to a boost-control / wastegate solenoid (a MAC-style
# duty valve bleeding wastegate dome / actuator pressure).
#   OPEN LOOP  : output duty = a per-gear feed-forward duty (C_DUTY[gear]).
#   CLOSED LOOP: output duty = that feed-forward + an integral trim that moves toward a
#                boost TARGET looked up by POWER MODE x GEAR x RPM, read from a sensor on a
#                repurposed O2 signal input.
# The target table lives in free flash at BTBL (3 power modes x 6 gears x 8 rpm zones, u16 raw
# ADC counts; the XDF shows it in kPa). RPM uses the nearest lower breakpoint (stepped zones,
# no interpolation). Power mode comes from fef01f74 (the active "PW 1-3", via a cal-set pointer).
#
# WHY THE O2 CIRCUIT: on a turbo build the stock narrowband O2 sensors are useless (and usually
# deleted), so BOTH halves of an O2 circuit are free: its low-side HEATER driver becomes the
# solenoid output, and its SIGNAL input becomes a 0-5 V boost-pressure input.
#
# Runs once per output-mapper cycle (~5 ms) by hooking the second call in FUN_5dc9a
# (0x5dca2: jarl 0x5dc64 -> jarl BOOST_TICK). Air-shift uses the PAIR output; boost uses the
# O2-heater output; they do not collide. Uses only caller-saved registers (r10-r19).
#
# *** OUTPUT AND INPUT CHANNELS ARE UNVERIFIED ON HARDWARE ***
# Output is isolated to OUT_ON / OUT_OFF (one spot); "Bench Test Output" finds its pin. OUTPUT
# POLARITY IS SET BY THE WIRING, not here. The boost-pressure input channel (C_PADDR) and the
# power-mode input (C_MADDR) are cal fields, so they are bench-adjustable without re-assembling.
# Closed loop ships OFF so neither input is on the critical path until proven. Ships DISABLED.

        .set B_RAM,   0xfebfe010        # scratch RAM (ALS 0xfebfe000..5, air-shift 0xfebfe008..a)
        .set R_PHASE, 0                 # u16 software-PWM phase counter (0..period-1)
        .set R_TRIM,  2                 # s16 closed-loop duty trim (added to the gear duty)

        .set CAL,     0x000bf030        # boost calibration block (see apply_patches.py BOOST_CAL)
        .set C_EN,    0                 # u8  0x80 = boost control enabled
        .set C_TEST,  1                 # u8  0x80 = bench test: hold the solenoid output asserted
        .set C_CL,    2                 # u8  0x80 = closed-loop trim enabled (needs inputs proven)
        .set C_PER,   4                 # u16 PWM period in task ticks (duty is 0..period)
        .set C_MINR,  6                 # u16 min rpm to run the solenoid (X/2.56); below -> off
        .set C_STEP,  8                 # u16 closed-loop trim step (duty ticks per period)
        .set C_PADDR, 10                # u16 boost-pressure input RAM address, low word (base 0xFEF00000)
        .set C_MADDR, 12                # u16 power-mode input RAM address, low word (default 0x1f74)
        .set C_DUTY,  14                # u16[6] per-gear open-loop duty (feed-forward), gears 1..6
        .set C_RPMAX, 26                # u16[8] RPM-zone breakpoints (ascending) for the target lookup

        .set BTBL,    0x000bf100        # boost target table: u16[3 modes][6 gears][8 rpm], raw ADC

        .set RPM,     0xfef0258c        # u16 engine rpm (X/2.56)        [confirmed]
        .set GEAR,    0xfef026c2         # u8 gear bitmask 1=N,2..0x40=6th [confirmed]
        .set IO_BASE, 0xfef0            # high half of the RAM/IO window; C_PADDR/C_MADDR give the low half

        # ---- OUTPUT PRIMITIVE (the only code that touches the physical solenoid output) ----
        # Candidate: O2-heater drive shadow fef020e4 bit0. Polarity is handled in the wiring; if the
        # bench shows a different pin, change the address/bit here (two lines), re-build, re-apply.
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
1:      # ---- enabled?  (disabled -> off = spring pressure, reset state)
        ld.bu   C_EN[r11], r12
        cmp     r13, r12                # r13 still 0x80
        be      2f
        st.h    r0, R_PHASE[r10]
        st.h    r0, R_TRIM[r10]
        OUT_OFF
        br      .Ldone
2:      # ---- min-rpm gate
        mov     RPM, r13
        ld.hu   0[r13], r15             # r15 = rpm
        ld.hu   C_MINR[r11], r12
        cmp     r12, r15
        bnl     3f
        st.h    r0, R_PHASE[r10]
        st.h    r0, R_TRIM[r10]
        OUT_OFF
        br      .Ldone
3:      # ---- gear -> index r18 (0..5); neutral / unknown -> off
        mov     GEAR, r13
        ld.bu   0[r13], r12
        cmp     2, r12
        be      .Lg0
        cmp     4, r12
        be      .Lg1
        cmp     8, r12
        be      .Lg2
        movea   0x10, r0, r13
        cmp     r13, r12
        be      .Lg3
        movea   0x20, r0, r13
        cmp     r13, r12
        be      .Lg4
        movea   0x40, r0, r13
        cmp     r13, r12
        be      .Lg5
        st.h    r0, R_PHASE[r10]
        OUT_OFF
        br      .Ldone
.Lg0:   mov     0, r18
        br      .Lgi
.Lg1:   mov     1, r18
        br      .Lgi
.Lg2:   mov     2, r18
        br      .Lgi
.Lg3:   mov     3, r18
        br      .Lgi
.Lg4:   mov     4, r18
        br      .Lgi
.Lg5:   mov     5, r18
.Lgi:
        # ---- feed-forward duty = CAL[C_DUTY + gi*2]
        mov     r18, r16
        shl     1, r16
        add     C_DUTY, r16
        add     r11, r16
        ld.hu   0[r16], r14             # r14 = feed-forward duty (kept to the PWM stage)
        # ---- closed loop?
        ld.bu   C_CL[r11], r12
        movea   0x80, r0, r13
        cmp     r13, r12
        bne     .Lnoloop
        # ---- power-mode index mi (0..2) from the cal-set mode pointer (value 1..3 -> 0..2)
        ld.hu   C_MADDR[r11], r12
        movhi   IO_BASE, r0, r16
        add     r12, r16
        ld.bu   0[r16], r12
        add     -1, r12
        cmp     0, r12
        bge     .Lmlo
        mov     0, r12
.Lmlo:  cmp     2, r12
        ble     .Lmhi
        mov     2, r12
.Lmhi:  mov     r12, r17                # r17 = mi
        # ---- rpm zone ri (0..7): nearest lower breakpoint in CAL[C_RPMAX]
        mov     0, r19                  # ri = 0
        mov     0, r12                  # k = 0
        mov     r11, r16
        add     C_RPMAX, r16            # &axis[0]
.Lrl:   ld.hu   0[r16], r13             # axis[k]
        cmp     r13, r15                # rpm - axis[k]
        bl      .Lrd                    # rpm < axis[k] -> stop (ri = last k that fit)
        mov     r12, r19                # ri = k
        add     1, r12
        add     2, r16
        cmp     8, r12
        bl      .Lrl
.Lrd:   # ---- index = ((mi*6)+gi)*8 + ri ; addr = BTBL + index*2
        mov     r17, r12
        shl     1, r12                  # 2*mi
        mov     r17, r13
        shl     2, r13                  # 4*mi
        add     r13, r12                # 6*mi
        add     r18, r12                # + gi
        shl     3, r12                  # * 8
        add     r19, r12                # + ri
        shl     1, r12                  # * 2 (bytes)
        mov     BTBL, r16
        add     r12, r16
        ld.hu   0[r16], r13             # r13 = this cell's target (raw ADC)
        # ---- measured pressure via the C_PADDR pointer
        ld.hu   C_PADDR[r11], r12
        movhi   IO_BASE, r0, r16
        add     r12, r16
        ld.hu   0[r16], r12             # r12 = measured raw
        ld.h    R_TRIM[r10], r17        # r17 = trim (signed)
        ld.hu   C_STEP[r11], r19        # r19 = step
        cmp     r13, r12                # measured - target
        bl      .Lunder                 # measured < target: more boost -> trim up
        sub     r19, r17                # back off
        br      .Lclamp
.Lunder:
        add     r19, r17
.Lclamp:
        ld.hu   C_PER[r11], r19         # clamp trim to +/- period
        cmp     r19, r17
        ble     .Lcl2
        mov     r19, r17
.Lcl2:  mov     r19, r16
        subr    r0, r16                 # r16 = -period
        cmp     r16, r17
        bge     .Lcl3
        mov     r16, r17
.Lcl3:  st.h    r17, R_TRIM[r10]
        add     r17, r14                # effective duty = feed-forward + trim
.Lnoloop:
        # ---- clamp effective duty to [0, period]
        cmp     0, r14
        bge     .Ldc2
        mov     0, r14
.Ldc2:  ld.hu   C_PER[r11], r19
        cmp     r19, r14
        ble     .Ldc3
        mov     r19, r14
.Ldc3:  # ---- software PWM: on while phase < duty, advance, wrap at period
        ld.hu   R_PHASE[r10], r15
        cmp     r14, r15
        bl      .Lon
        OUT_OFF
        br      .Ladv
.Lon:   OUT_ON
.Ladv:  add     1, r15
        ld.hu   C_PER[r11], r19
        cmp     r19, r15
        bl      .Lstore
        mov     0, r15
.Lstore:
        st.h    r15, R_PHASE[r10]
.Ldone:
        dispose 0, {lp}, [lp]
