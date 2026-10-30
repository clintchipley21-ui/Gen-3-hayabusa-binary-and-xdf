# Rolling anti-lag for Hayabusa Gen3 5JCZSJ40  (RH850 / v850e3v5)
# -----------------------------------------------------------------------------
# TRIGGER: hold the cruise-control SET button. The meter sends the SET long-hold flag in
# CAN frame 0x1D1 byte 4 (bit 0x02), which the ECU mirrors to RAM fef02443. While that bit is
# held, anti-lag captures the engine RPM at the moment of the press and holds it with an
# all-cylinder spark cut (fuel stays on); releasing SET drops anti-lag and returns spark.
# CRUISE IS PRESERVED: if the cruise system is switched ON (fef02726 bit0, the cruise ON/OFF
# state read by FUN_751da), anti-lag does NOT arm, so SET keeps its normal cruise function.
# Turn cruise off to use the SET button for anti-lag.
# (We deliberately do NOT gate on 0x1D1 byte0 / fef0243f: a riding cangaroo trace shows byte0 is
#  a composite - it goes to 0xF0 for 98.7% of SET long-hold frames even with cruise OFF, and takes
#  a third value 0x11 while riding - so gating "byte0 != 0 = cruise on" would let the SET-hold
#  trigger disarm itself. The internal computed flag fef02726 bit0 is the clean cruise state.)
#   - Capture RPM on the press, clamped to [Min RPM, Max RPM].
#   - Safety: needs coolant >= Min Coolant; latches off after Max Active Time until released.
# (The old START+WOT trigger and the grip/speed gates are gone; "Capture/Release Grip Angle"
#  and "Min Rolling Speed" in the XDF are UNUSED in this SET-hold variant.)
# UNVERIFIED ON HARDWARE. Spark-cut anti-lag with fuel on makes big EGT - use short holds.
        .set ALS_RAM,   0xfebfe000      # flags(u8) +0, cap(u16) +2, timer(u16) +4
        .set CAL,       0x000bf000
        .set C_EN,      0               # u8  0x80 = enabled
        .set C_ECT,     1               # u8  min coolant raw
        .set C_SPD,     2               # u16 (unused here) min front wheel speed
        .set C_WOTON,   4               # u16 (unused here) capture grip angle
        .set C_WOTOFF,  6               # u16 (unused here) release grip angle
        .set C_RPMMIN,  8               # u16 min capture rpm (X/2.56)
        .set C_RPMMAX,  10              # u16 max capture rpm
        .set C_HYST,    12              # u16 hysteresis (rpm counts)
        .set C_TMAX,    14              # u16 max active time (5 ms ticks)

        .set SETHOLD,   0xfef02443      # 0x1D1 byte4 button byte; bit 0x02 = SET long-hold
        .set CRUISE_ON, 0xfef02726      # bit0 = cruise system ON (FUN_751da); gate ALS off when set

        .section .als_code,"ax"
        .globl ALS_TICK, ALS_LIMIT, ALS_IS_ACTIVE
# ---------------------------------------------------------------- 5 ms task
ALS_TICK:
        mov     ALS_RAM, r10
        mov     CAL, r11
        ld.bu   C_EN[r11], r12
        movea   0x80, r0, r13
        cmp     r13, r12
        bne     .Ldisarm
        # ---- TRIGGER: cruise SET long-hold (fef02443 bit1 = 0x02). Release -> .Ldisarm (stop).
        mov     SETHOLD, r13
        tst1    1, 0[r13]
        bz      .Ldisarm
        # ---- cruise gate: if the cruise system is ON, leave SET to cruise (no anti-lag)
        mov     CRUISE_ON, r13
        tst1    0, 0[r13]
        bnz     .Ldisarm
        # ---- coolant >= min (safety)
        mov     0xfef026bd, r13
        ld.bu   0[r13], r13
        ld.bu   C_ECT[r11], r14
        cmp     r14, r13
        bl      .Ldisarm
        # ---- timed out? stay inactive until SET is released
        tst1    1, 0[r10]
        bz      2f
        clr1    0, 0[r10]
        br      .Ldone
2:      tst1    0, 0[r10]
        bnz     .Lactive
        # ---- not active: capture rpm on the press, clamped to [min, max]
        mov     0xfef0258c, r15
        ld.hu   0[r15], r15             # rpm
        ld.hu   C_RPMMIN[r11], r14
        cmp     r14, r15
        bnl     8f                      # rpm >= min: keep
        mov     r14, r15                # else clamp up to min
8:      ld.hu   C_RPMMAX[r11], r14
        cmp     r14, r15
        bl      9f                      # rpm < max: keep
        mov     r14, r15                # else clamp down to max
9:      st.h    r15, 2[r10]             # captured target rpm
        set1    0, 0[r10]               # active
        br      .Ldone
.Lactive:
        # ---- hold: accumulate active time, latch off at C_TMAX (released by letting go of SET)
        ld.hu   4[r10], r15
        add     1, r15
        st.h    r15, 4[r10]
        ld.hu   C_TMAX[r11], r14
        cmp     r14, r15
        bl      .Ldone
        movea   2, r0, r15              # timeout: latch inactive until SET released
        st.b    r15, 0[r10]
        br      .Ldone
.Ldisarm:
        st.b    r0, 0[r10]
        st.h    r0, 4[r10]
.Ldone:
        jr      FUN_5BDB4                 # tail-call the original FUN_5BDB4

        .org    0xd6                      # pin ALS_LIMIT at 0xBE0D6 so the stock hooks still land
# ---------------------------------------------------------------- ignition-cut limiter (replaces FUN_2C700)
ALS_LIMIT:
        prepare {lp}, 0
        zxh     r6
        mov     ALS_RAM, r10
        tst1    0, 0[r10]
        bz      4f
        ld.hu   2[r10], r19             # ON  = captured rpm
        mov     CAL, r11
        ld.hu   C_HYST[r11], r12
        mov     r19, r18
        sub     r12, r18                # OFF = cap - hyst
        bnl     5f
        mov     r0, r18
        br      5f
4:      movhi   0x15, r0, r18
        ld.hu   0x42d0[r18], r18        # stock OFF 0x1542D0
        movhi   0x15, r0, r19
        ld.hu   0x42d2[r19], r19        # stock ON  0x1542D2
5:      mov     0xfef00a1e, r1
        cmp     r18, r6
        bl      6f
        cmp     r19, r6
        bl      7f
        set1    1, 0[r1]
        br      7f
6:      clr1    1, 0[r1]
7:      tst1    1, 0[r1]
        setf    nz, r6
        jarl    FUN_2C396, lp
        dispose 0, {lp}, [lp]

# ---------------------------------------------------------------- used by FUN_525EE table select
ALS_IS_ACTIVE:
        mov     ALS_RAM, r10
        ld.bu   0[r10], r10
        andi    1, r10, r10
        jmp     [lp]
