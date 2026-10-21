#include "race_control.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
    uint8_t bytes[RACE_PROFILE_SIZE];
    race_config c, bad;
    race_state s;
    race_outputs o;
    race_inputs in={0};
    FILE *f;
    unsigned g, i;
    assert(argc == 2);
    f=fopen(argv[1],"rb"); assert(f);
    assert(fread(bytes,1,sizeof(bytes),f)==sizeof(bytes)); fclose(f);
    assert(race_decode(bytes,sizeof(bytes),&c));
    assert(!c.enabled && c.pwm_hz==31 && c.o2_channel==0);
    assert(!race_decode(bytes,sizeof(bytes)-1,&bad));
    bytes[0]^=1; assert(!race_decode(bytes,sizeof(bytes),&bad)); bytes[0]^=1;
    assert(race_gm55567257_kpa_x100(500)==2000);
    assert(race_gm55567257_kpa_x100(4500)==27000);
    assert(race_haltech150_psi_x100(500)==0);
    assert(race_haltech150_psi_x100(2500)==7500);
    assert(race_haltech150_psi_x100(4500)==15000);
    for (g=1; g<RACE_GEARS; ++g) for (i=0; i<RACE_RPM_POINTS; ++i) {
        c.target_hat[g][i]=2000; c.base_duty[g][i]=3000;
    }
    c.kp=100; c.ki=10;
    in.now_ms=100; in.rpm=5000; in.grip=4000; in.ect=800;
    in.map_mv=2000; in.hat_mv=500; in.map_valid=1; in.hat_valid=1;
    in.gear=1; in.running=1; in.armed=1;
    race_init(&s); race_tick(&c,&in,&s,&o);
    assert(o.duty==0 && !o.output_authorized); /* disabled */
    c.enabled=0x80;
    race_tick(&c,&in,&s,&o); assert(o.duty==5000 && o.output_authorized && !o.faults);
    in.now_ms+=10; race_tick(&c,&in,&s,&o); assert(o.duty==5002);
    in.hat_mv=1300; /* 30 PSI; target 20 -> duty must fall */
    in.now_ms+=10; race_tick(&c,&in,&s,&o); assert(o.duty<3000);
    in.als_active=1; in.now_ms+=10; race_tick(&c,&in,&s,&o);
    assert(!o.duty && !o.output_authorized && !s.integral_milli_bp);
    in.als_active=0; in.shift_active=1; race_tick(&c,&in,&s,&o); assert(!o.duty);
    in.shift_active=0; in.gear=0; race_tick(&c,&in,&s,&o); assert(!o.duty);
    in.gear=7; race_tick(&c,&in,&s,&o); assert(!o.duty);
    in.gear=1; in.map_mv=4500; c.map_limit=26999;
    race_tick(&c,&in,&s,&o);
    assert((o.faults&RACE_OVERBOOST) && !o.duty && o.request_engine_cut);
    in.map_mv=2000; race_tick(&c,&in,&s,&o); assert(o.faults&RACE_OVERBOOST);
    assert(!race_reset_faults(&s,&in));
    in.running=0; assert(!race_reset_faults(&s,&in));
    in.armed=0; assert(race_reset_faults(&s,&in));
    in.running=1; in.armed=1; c.map_limit=27000;
    in.hat_age_ms=51; race_tick(&c,&in,&s,&o); assert((o.faults&RACE_STALE) && !o.duty);
    race_init(&s); in.hat_age_ms=0; in.hat_mv=0;
    race_tick(&c,&in,&s,&o); assert((o.faults&RACE_SENSOR) && !o.duty);
    race_init(&s); in.hat_mv=1900; /* 52.5 PSI, limit 50 */
    race_tick(&c,&in,&s,&o); assert((o.faults&RACE_HAT_OVERPRESSURE) && !o.duty);
    race_init(&s); in.hat_mv=500; in.hat_valid=0;
    race_tick(&c,&in,&s,&o); assert(o.faults&RACE_SENSOR);
    race_init(&s); in.hat_valid=1; in.now_ms=100;
    race_tick(&c,&in,&s,&o); in.now_ms=200;
    race_tick(&c,&in,&s,&o); assert((o.faults&RACE_TIMING) && !o.duty);
    race_init(&s); in.now_ms=0xfffffff8u;
    race_tick(&c,&in,&s,&o); in.now_ms=8;
    race_tick(&c,&in,&s,&o); assert(!o.faults && o.duty>0); /* time wrap */
    bad=c; bad.rpm[2]=bad.rpm[1]; assert(!race_config_valid(&bad));
    race_init(&s); race_tick(&bad,&in,&s,&o); assert((o.faults&RACE_CONFIG) && !o.duty);
    bad=c; bad.duty_max=9001; assert(!race_config_valid(&bad));
    bad=c; bad.hat_limit=12001; assert(!race_config_valid(&bad));
    bad=c; bad.pwm_hz=100; assert(!race_config_valid(&bad));
    bad=c; bad.target_hat[0][0]=1; assert(!race_config_valid(&bad));
    /* Saturating positive error cannot wind up the integrator. */
    race_init(&s); c.kp=1000; c.ki=1000; in.now_ms=0;
    for (i=0; i<1000; ++i) {
        in.now_ms+=10; race_tick(&c,&in,&s,&o); assert(o.duty==9000 && !o.faults);
    }
    assert(s.integral_milli_bp==0);
    in.hat_mv=1300; in.now_ms+=10; race_tick(&c,&in,&s,&o); assert(!o.duty);
    /* RPM interpolation and clamps are evaluated from a real table. */
    for (i=0; i<RACE_RPM_POINTS; ++i) c.target_hat[1][i]=(uint16_t)(i*100);
    assert(race_curve(c.rpm,c.target_hat[1],5500)==550);
    assert(race_curve(c.rpm,c.target_hat[1],20000)==1500);
    /* Maximum validated PI product stays within int32 on the target. */
    c.hat_limit=12000; c.hat_mv_min=100; c.max_step_ms=100;
    for (i=0; i<RACE_RPM_POINTS; ++i) c.target_hat[1][i]=12000;
    race_init(&s); in.hat_mv=100; in.now_ms=0;
    race_tick(&c,&in,&s,&o); in.now_ms=100;
    race_tick(&c,&in,&s,&o); assert(o.duty==9000 && !o.faults);
    puts("native controller scenarios passed (profile decode, pressure units, PI, gates, faults, timer wrap, anti-windup)");
    return 0;
}
