/* Portable integration core. No ECU addresses, hooks or physical output driver. */
#ifndef RACE_CONTROL_H
#define RACE_CONTROL_H
#include <stdint.h>
#define RACE_RPM_POINTS 16
#define RACE_GEARS 7
#define RACE_PROFILE_SIZE 576
enum race_fault { RACE_OK=0, RACE_CONFIG=1, RACE_SENSOR=2, RACE_STALE=4,
                  RACE_OVERBOOST=8, RACE_HAT_OVERPRESSURE=16, RACE_TIMING=32 };
typedef struct {
    uint16_t rpm[RACE_RPM_POINTS];
    uint16_t target_hat[RACE_GEARS][RACE_RPM_POINTS]; /* PSI * 100 */
    uint16_t base_duty[RACE_GEARS][RACE_RPM_POINTS];  /* 0..10000 */
    uint16_t pwm_hz, duty_min, duty_max, map_limit, hat_limit;
    uint16_t kp, ki, min_rpm, min_grip, map_mv_min, map_mv_max;
    uint16_t hat_mv_min, hat_mv_max, max_age_ms, max_step_ms, min_ect;
    uint8_t enabled, o2_channel;
} race_config;
typedef struct {
    uint32_t now_ms;
    uint16_t rpm, grip; /* RPM, degrees * 100 */
    int16_t ect;       /* degrees C * 10 */
    uint16_t map_mv, hat_mv, map_age_ms, hat_age_ms;
    uint8_t gear, running, armed, map_valid, hat_valid, als_active, shift_active;
} race_inputs;
typedef struct {
    uint32_t last_ms;
    int32_t integral_milli_bp;
    uint16_t faults;
    uint8_t initialized;
} race_state;
typedef struct {
    uint16_t duty, pwm_hz, faults, target_hat;
    int32_t map_kpa_x100, hat_psi_x100;
    uint8_t request_engine_cut, output_authorized;
} race_outputs;
int race_decode(const uint8_t *bytes, uint32_t length, race_config *config);
int race_config_valid(const race_config *config);
int32_t race_gm55567257_kpa_x100(uint16_t millivolts);
int32_t race_haltech150_psi_x100(uint16_t millivolts);
uint16_t race_curve(const uint16_t *axis, const uint16_t *values, uint16_t x);
/* Always starts OFF. Fault reset is allowed only with engine stopped and disarmed. */
void race_init(race_state *state);
int race_reset_faults(race_state *state, const race_inputs *inputs);
void race_tick(const race_config *config, const race_inputs *inputs,
               race_state *state, race_outputs *outputs);
#endif
