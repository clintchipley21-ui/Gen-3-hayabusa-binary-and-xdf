#include "race_control.h"
#include <string.h>

static uint16_t u16(const uint8_t *p) { return (uint16_t)(p[0] | ((uint16_t)p[1] << 8)); }
static int32_t clamp32(int32_t value, int32_t low, int32_t high) {
    return value < low ? low : value > high ? high : (int32_t)value;
}
int32_t race_gm55567257_kpa_x100(uint16_t mv) {
    return ((int32_t)mv * 625 + 50) / 100 - 1125;
}
int32_t race_haltech150_psi_x100(uint16_t mv) {
    return ((int32_t)mv - 500) * 15000 / 4000;
}
uint16_t race_curve(const uint16_t *axis, const uint16_t *values, uint16_t x) {
    unsigned i;
    if (x <= axis[0]) return values[0];
    for (i=1; i<RACE_RPM_POINTS; ++i) {
        if (x <= axis[i]) {
            int32_t delta = (int32_t)values[i] - values[i-1];
            return (uint16_t)((int32_t)values[i-1] +
                delta * (x-axis[i-1]) / (axis[i]-axis[i-1]));
        }
    }
    return values[RACE_RPM_POINTS-1];
}
int race_config_valid(const race_config *c) {
    unsigned g, i;
    if (c->enabled != 0 && c->enabled != 0x80) return 0;
    if (c->o2_channel > 1 || c->pwm_hz != 31 || c->duty_min < 1000 ||
        c->duty_max > 9000 || c->duty_min > c->duty_max ||
        c->map_limit < 10000 || c->map_limit > 30000 ||
        !c->hat_limit || c->hat_limit > 12000 ||
        c->kp > 1000 || c->ki > 1000 || c->min_rpm < 500 ||
        c->min_grip > 11000 || c->min_ect > 1500 ||
        c->map_mv_min < 100 || c->map_mv_max > 4900 ||
        c->map_mv_min >= c->map_mv_max || c->hat_mv_min < 100 ||
        c->hat_mv_max > 4900 || c->hat_mv_min >= c->hat_mv_max ||
        !c->max_age_ms || c->max_age_ms > 100 ||
        !c->max_step_ms || c->max_step_ms > 100) return 0;
    for (i=1; i<RACE_RPM_POINTS; ++i) if (c->rpm[i] <= c->rpm[i-1]) return 0;
    for (g=0; g<RACE_GEARS; ++g) for (i=0; i<RACE_RPM_POINTS; ++i) {
        if (c->target_hat[g][i] > c->hat_limit || c->base_duty[g][i] > c->duty_max) return 0;
        if (g == 0 && (c->target_hat[g][i] || c->base_duty[g][i])) return 0;
    }
    return 1;
}
int race_decode(const uint8_t *b, uint32_t length, race_config *c) {
    unsigned g, i;
    memset(c, 0, sizeof(*c));
    if (length != RACE_PROFILE_SIZE || memcmp(b, "RACEWG01", 8) ||
        u16(b+8) != RACE_PROFILE_SIZE || u16(b+10) != 1) return 0;
    c->enabled=b[12]; c->o2_channel=b[13];
    c->pwm_hz=u16(b+14); c->duty_min=u16(b+16); c->duty_max=u16(b+18);
    c->map_limit=u16(b+20); c->hat_limit=u16(b+22); c->kp=u16(b+24); c->ki=u16(b+26);
    c->min_rpm=u16(b+28); c->min_grip=u16(b+30);
    c->map_mv_min=u16(b+32); c->map_mv_max=u16(b+34);
    c->hat_mv_min=u16(b+36); c->hat_mv_max=u16(b+38);
    c->max_age_ms=u16(b+40); c->max_step_ms=u16(b+42); c->min_ect=u16(b+44);
    for (i=0; i<RACE_RPM_POINTS; ++i) c->rpm[i]=u16(b+64+i*2);
    for (g=0; g<RACE_GEARS; ++g) {
        if (u16(b+96+g*2) != g) return 0;
        for (i=0; i<RACE_RPM_POINTS; ++i) {
            c->target_hat[g][i]=u16(b+128+(g*RACE_RPM_POINTS+i)*2);
            c->base_duty[g][i]=u16(b+352+(g*RACE_RPM_POINTS+i)*2);
        }
    }
    return race_config_valid(c);
}
void race_init(race_state *s) { memset(s, 0, sizeof(*s)); }
int race_reset_faults(race_state *s, const race_inputs *in) {
    if (in->running || in->armed) return 0;
    race_init(s); return 1;
}
void race_tick(const race_config *c, const race_inputs *in, race_state *s, race_outputs *out) {
    uint32_t dt=0;
    int32_t error, proportional, integral, requested;
    uint16_t base;
    memset(out, 0, sizeof(*out));
    out->pwm_hz=31;
    out->map_kpa_x100=race_gm55567257_kpa_x100(in->map_mv);
    out->hat_psi_x100=race_haltech150_psi_x100(in->hat_mv);
    if (!race_config_valid(c)) s->faults |= RACE_CONFIG;
    if (s->initialized) dt=in->now_ms-s->last_ms; /* unsigned wrap intentional */
    s->last_ms=in->now_ms;
    if (!c->enabled) { s->integral_milli_bp=0; s->initialized=0; goto done; }
    if (s->faults & RACE_CONFIG) goto done;
    if (!in->map_valid || !in->hat_valid || in->map_mv < c->map_mv_min ||
        in->map_mv > c->map_mv_max || in->hat_mv < c->hat_mv_min ||
        in->hat_mv > c->hat_mv_max) s->faults |= RACE_SENSOR;
    if (in->map_age_ms > c->max_age_ms || in->hat_age_ms > c->max_age_ms) s->faults |= RACE_STALE;
    if (out->map_kpa_x100 > c->map_limit) s->faults |= RACE_OVERBOOST;
    if (out->hat_psi_x100 > c->hat_limit) s->faults |= RACE_HAT_OVERPRESSURE;
    if (s->initialized && dt > c->max_step_ms) s->faults |= RACE_TIMING;
    if (s->faults) goto done;
    if (!in->armed || !in->running || in->gear < 1 || in->gear > 6 ||
        in->rpm < c->min_rpm || in->grip < c->min_grip || in->ect < c->min_ect ||
        in->als_active || in->shift_active) {
        s->integral_milli_bp=0; s->initialized=0; goto done;
    }
    out->target_hat=race_curve(c->rpm, c->target_hat[in->gear], in->rpm);
    if (!out->target_hat) { s->integral_milli_bp=0; s->initialized=0; goto done; }
    base=race_curve(c->rpm, c->base_duty[in->gear], in->rpm);
    error=(int32_t)out->target_hat-out->hat_psi_x100;
    proportional=(int32_t)c->kp*error/100;
    /* Validated bounds: |error| <= 13500, ki <= 1000, dt <= 100 ms.
       Product <= 1.35e9; integral addition <= 22.5e6. No 64-bit helper/ABI needed. */
    integral=clamp32(s->integral_milli_bp + (int32_t)c->ki*error*(int32_t)dt/100,
                     -(int32_t)c->duty_max*1000, (int32_t)c->duty_max*1000);
    requested=(int32_t)base+proportional+integral/1000;
    /* Do not integrate farther into either saturation rail. */
    if (!((requested > c->duty_max && error > 0) || (requested < 0 && error < 0)))
        s->integral_milli_bp=integral;
    requested=(int32_t)base+proportional+s->integral_milli_bp/1000;
    out->duty=(uint16_t)clamp32(requested, 0, c->duty_max);
    if (out->duty && out->duty < c->duty_min) out->duty=c->duty_min;
    out->output_authorized=1;
    s->initialized=1;
done:
    out->faults=s->faults;
    if (s->faults) {
        s->integral_milli_bp=0;
        out->duty=0; out->output_authorized=0;
        out->request_engine_cut=in->running ? 1 : 0;
    }
}
