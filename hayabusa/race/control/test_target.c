/* Freestanding target self-test; run in Ghidra, never installed in ECU firmware.
   profile_fixture.h is generated from a prepared image's 576-byte profile. */
#include "race_control.h"
#include "freestanding/string.h"
#include "profile_fixture.h"
#define CHECK(test) do { if (!(test)) return __LINE__; } while (0)
unsigned race_target_selftest(void) {
    race_config c;
    race_inputs in;
    race_outputs out;
    race_state state;
    unsigned g,i;
    CHECK(race_decode(profile_fixture,RACE_PROFILE_SIZE,&c));
    CHECK(c.enabled==0 && c.pwm_hz==31);
    CHECK(race_gm55567257_kpa_x100(4500)==27000);
    CHECK(race_haltech150_psi_x100(2500)==7500);
    memset(&in,0,sizeof(in));
    in.rpm=5000; in.grip=4000; in.ect=800; in.map_mv=2000;
    in.hat_mv=500; in.gear=1; in.running=1; in.armed=1;
    in.map_valid=1; in.hat_valid=1;
    race_init(&state);
    race_tick(&c,&in,&state,&out); CHECK(!out.duty);
    c.enabled=0x80; c.kp=100; c.ki=10;
    for (g=1;g<RACE_GEARS;++g) for (i=0;i<RACE_RPM_POINTS;++i) {
        c.target_hat[g][i]=2000; c.base_duty[g][i]=3000;
    }
    race_tick(&c,&in,&state,&out); CHECK(out.duty==5000 && !out.faults);
    in.now_ms=10; race_tick(&c,&in,&state,&out); CHECK(out.duty==5002);
    in.als_active=1; in.now_ms=20; race_tick(&c,&in,&state,&out); CHECK(!out.duty);
    in.als_active=0; in.shift_active=1; race_tick(&c,&in,&state,&out); CHECK(!out.duty);
    in.shift_active=0; in.map_mv=4500; c.map_limit=26999;
    race_tick(&c,&in,&state,&out);
    CHECK((out.faults&RACE_OVERBOOST) && !out.duty && out.request_engine_cut);
    CHECK(!race_reset_faults(&state,&in));
    in.running=0; in.armed=0; CHECK(race_reset_faults(&state,&in));
    in.running=1; in.armed=1; in.map_mv=2000; c.map_limit=27000;
    in.hat_age_ms=51; race_tick(&c,&in,&state,&out); CHECK(out.faults&RACE_STALE);
    race_init(&state); in.hat_age_ms=0; in.hat_valid=0;
    race_tick(&c,&in,&state,&out); CHECK(out.faults&RACE_SENSOR);
    race_init(&state); in.hat_valid=1; in.now_ms=0xfffffff8u;
    race_tick(&c,&in,&state,&out); in.now_ms=8;
    race_tick(&c,&in,&state,&out); CHECK(!out.faults && out.duty>0);
    c.rpm[2]=c.rpm[1]; race_init(&state);
    race_tick(&c,&in,&state,&out); CHECK((out.faults&RACE_CONFIG) && !out.duty);
    return 0;
}
