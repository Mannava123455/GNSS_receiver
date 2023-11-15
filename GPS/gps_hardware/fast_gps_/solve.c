#include "solve.h"


static void snapshot_timing(struct Snapshot *s)
 {
    int i;
    static int heading = 0;
    
    
    /* Clear out the snapshot structure */
    memset(s,0,sizeof(struct Snapshot));
    s->sample_count_h = sample_count>>32;
    s->sample_count_l = sample_count & 0xFFFFFFFF;
    
    
    if(heading == 0) {
      // printf("Id,  State, Orbt, Time, WeekNo, FrameOfWeek, msOfFrame, ChipOfCode, fracOfChip\n");
    }
    heading++;
    if(heading == 49)
        heading = 0;
        for(i = 0; i < N_SV; i++) {
            struct Space_vehicle *sv;
            sv = space_vehicles+i;
            s->entries[i].id = sv->id;
            switch(sv->state) {
                case state_acquiring:
                    s->entries[i].state |= SNAPSHOT_STATE_ACQUIRE;
                    break;
                case state_tracking:
                    s->entries[i].state |= SNAPSHOT_STATE_TRACK;
                    break;
                case state_locked:
                    s->entries[i].state |= SNAPSHOT_STATE_LOCKED;
                    break;
                default:
                    break;
            }
            if(sv->nav_orbit.orbit_valid) 
                s->entries[i].state |= SNAPSHOT_STATE_ORBIT_VALID;


            if(sv->nav_time.time_good) 
                s->entries[i].state |= SNAPSHOT_STATE_TIME_VALID;

            s->entries[i].lock_ms_of_frame      = sv->lock.ms_of_frame;
            s->entries[i].lock_ms_of_bit        = sv->lock.ms_of_bit;
            s->entries[i].lock_code_nco         = sv->lock.code_nco;
            s->entries[i].nav_week_no           = sv->nav_time.week_no;
            s->entries[i].nav_subframe_of_week  = sv->navdata.subframe_of_week;
            s->entries[i].nav_subframe_in_frame = sv->navdata.subframe_in_frame;
            s->entries[i].nav_valid_bits        = sv->navdata.valid_bits;
        }
        //fwrite(s, sizeof(struct Snapshot), 1, snapshot_file);
    
#if SHOW_TIMING_SNAPSHOT_DETAILS            
    for(i = 0; i < N_SV; i++) {
        struct Space_vehicle *sv;
        int id;

        sv = space_vehicles+i;
        id = sv->id;
        printf("%02i,",id);
        switch(sv->state) {
            case state_acquiring:
                printf("ACQUIRE, ");
                break;
            case state_tracking:
                printf("  TRACK, ");
                break;
            case state_locked:
                printf(" LOCKED, ");
                break;
            default:
                printf(" ??????, ");
                break;
        }
        if(sv->nav_orbit.orbit_valid) 

            printf("YES,");
        else
            printf(" NO,");

        if(sv->nav_time.time_good) 
            printf("YES,");
        else
            printf(" NO,");

        printf(" %6i,      %6i,      %4i,       %4i,         %2i %1i  %2i %2i %c%c%c%c%c\n",
            sv->nav_time.week_no,
            sv->navdata.subframe_of_week,
            sv->lock.ms_of_frame,
            (sv->lock.code_nco>>22),
            (sv->lock.code_nco>>16)&0x3f,
            sv->navdata.subframe_in_frame,
            sv->navdata.valid_bits-2,
            sv->lock.ms_of_bit,
            (sv->navdata.valid_subframe[1] ? '1' : '.'),
            (sv->navdata.valid_subframe[2] ? '2' : '.'),
            (sv->navdata.valid_subframe[3] ? '3' : '.'),
            (sv->navdata.valid_subframe[4] ? '4' : '.'),
            (sv->navdata.valid_subframe[5] ? '5' : '.')
            );
    }

    printf("\n");
#endif
}



static double  orbit_ecc_anom(struct Space_vehicle *sv, double t) 
{
    int    iterations  = 200;
    double delta       = pow(10,-10);
    double estimate, correction, semi_major_axis,     computed_mean_motion;
    double time_from_ephemeris,  correct_mean_motion, mean_anomaly;

    semi_major_axis      = sv->nav_orbit.sqrt_A * sv->nav_orbit.sqrt_A;
    computed_mean_motion = sqrt(mu / pow(semi_major_axis,3.0));

    time_from_ephemeris  = t - sv->nav_orbit.time_of_ephemeris;
    if(time_from_ephemeris >  302400) time_from_ephemeris  -= 604800;
    if(time_from_ephemeris < -302400) time_from_ephemeris  += 604800;
    correct_mean_motion  = computed_mean_motion + sv->nav_orbit.delta_n;

    /* Add on how much we have moved through the orbit since ephemeris */
    mean_anomaly         = sv->nav_orbit.mean_motion_at_ephemeris + correct_mean_motion * time_from_ephemeris;

    /* First estimate */
    estimate   = (sv->nav_orbit.e<0.8) ? mean_anomaly :  PI;
    correction = estimate - (mean_anomaly + sv->nav_orbit.e*sin(mean_anomaly));

    /* Solve iteratively */
    while ((fabs(correction)>delta) && iterations > 0) 
    {
        double last = estimate;
        estimate  = mean_anomaly  + sv->nav_orbit.e * sin(estimate);
        correction = estimate - last;
        iterations--;
    }

    if(iterations == 0) {
        printf("Error calculating Eccentric Anomaly\n");
    }
    return estimate;
}


static void sv_calc_corrected_time(int i) 
{
    double delta_t, delta_tr, ek, time_correction;
    struct Space_vehicle *sv;    
    sv = space_vehicles+i;
    sv->pos_t_valid = 0;

    /* Calulate the time for the adjustment */
    delta_t = sv->time_raw - sv->nav_time.reference_time;
    if(delta_t >  302400)  delta_t -= 604800;
    if(delta_t < -302400)  delta_t += 604800;

    /* Relativistic term */
    ek = orbit_ecc_anom(sv, sv->time_raw);

    delta_tr = -4.442807633e-10 * sv->nav_orbit.e * sv->nav_orbit.sqrt_A * sin(ek);

    time_correction = sv->nav_time.correction_f0 
                    + (sv->nav_time.correction_f1 * delta_t) 
                    + (sv->nav_time.correction_f2 * delta_t * delta_t) 
                    + delta_tr
                    - sv->nav_time.group_delay;
    sv->pos_t = sv->time_raw - time_correction;
    sv->pos_t_valid = 1;
    return;

}


static int orbit_calc_position(struct Space_vehicle *sv, struct Location *l)
{
  double time_from_ephemeris,   semi_major_axis;
  double ek, true_anomaly,      corrected_argument_of_latitude;
  double argument_of_latitude,  argument_of_latitude_correction;
  double radius_correction,     corrected_radius;
  double correction_of_inclination;
  double pos_in_orbial_plane_x, pos_in_orbial_plane_y;
  double corrected_inclination, corrected_angle_of_ascending_node;
  
  /***********************
  * Calculate orbit
  ***********************/
  time_from_ephemeris  = sv->pos_t - sv->nav_orbit.time_of_ephemeris;
  if(time_from_ephemeris >  302400) time_from_ephemeris  -= 604800;
  if(time_from_ephemeris < -302400) time_from_ephemeris  += 604800;

  semi_major_axis      = sv->nav_orbit.sqrt_A * sv->nav_orbit.sqrt_A;
  ek = orbit_ecc_anom(sv, sv->pos_t);

  /* Now calculate the first approximation of the latitude */
  true_anomaly = atan2( sqrt(1-sv->nav_orbit.e * sv->nav_orbit.e) * sin(ek), cos(ek) - sv->nav_orbit.e);
  argument_of_latitude = true_anomaly + sv->nav_orbit.w;

  /*****************************************
  * Second Harmonic Perbturbations 
  *****************************************/
  argument_of_latitude_correction = sv->nav_orbit.Cus * sin(2*argument_of_latitude) 
                                  + sv->nav_orbit.Cuc * cos(2*argument_of_latitude);

  radius_correction               = sv->nav_orbit.Crc * cos(2*argument_of_latitude) 
                                  + sv->nav_orbit.Crs * sin(2*argument_of_latitude);
  
  correction_of_inclination       = sv->nav_orbit.Cic * cos(2*argument_of_latitude) 
                                  + sv->nav_orbit.Cis * sin(2*argument_of_latitude);

  corrected_argument_of_latitude  = argument_of_latitude + argument_of_latitude_correction;
  corrected_radius                = semi_major_axis * (1- sv->nav_orbit.e * cos(ek)) + radius_correction;
  corrected_inclination           = sv->nav_orbit.inclination_at_ephemeris + correction_of_inclination 
                                  + sv->nav_orbit.idot*time_from_ephemeris;

  pos_in_orbial_plane_x = corrected_radius * cos(corrected_argument_of_latitude);
  pos_in_orbial_plane_y = corrected_radius * sin(corrected_argument_of_latitude);
  

  corrected_angle_of_ascending_node = sv->nav_orbit.omega_0
                                    + (sv->nav_orbit.omega_dot - omegaDot_e)*time_from_ephemeris 
                                    - omegaDot_e * sv->nav_orbit.time_of_ephemeris;

  /******************************************************
  * Project into Earth Centered, Earth Fixed coordinates
  ******************************************************/
  l->x = pos_in_orbial_plane_x * cos(corrected_angle_of_ascending_node)
       - pos_in_orbial_plane_y * cos(corrected_inclination) * sin(corrected_angle_of_ascending_node);
  l->y = pos_in_orbial_plane_x * sin(corrected_angle_of_ascending_node) 
       + pos_in_orbial_plane_y * cos(corrected_inclination) * cos(corrected_angle_of_ascending_node);
  l->z = pos_in_orbial_plane_y * sin(corrected_inclination);
  l->time = sv->pos_t;

  return 1;
}

static int sv_calc_location(int id, struct Location *l)
{  
    l->time = space_vehicles[id].pos_t;
    orbit_calc_position(space_vehicles+id, l);
    return 1;
}


int A_solve(int chans, struct Location *sv_l, struct Location *p) {
    int i, j, r, c;

    double t_tx[NUM_CHANS]; // Clock replicas in seconds since start of week

    double x_sv[NUM_CHANS],
           y_sv[NUM_CHANS],
           z_sv[NUM_CHANS];
  
    double t_pc;  // Uncorrected system time when clock replica snapshots taken
    double t_rx;    // Corrected GPS time

    double dPR[NUM_CHANS]; // Pseudo range error

    double jac[NUM_CHANS][4], ma[4][4], mb[4][4], mc[4][NUM_CHANS], md[4];

    double weight[NUM_CHANS];

    p->x = p->y = p->z = p->time = t_pc = 0.0;

    for (i=0; i<chans && i < NUM_CHANS; i++) {
        weight[i] = 1.0;
        x_sv[i]   = sv_l[i].x;
        y_sv[i]   = sv_l[i].y;
        z_sv[i]   = sv_l[i].z;
        t_tx[i]   = sv_l[i].time;
        t_pc     += sv_l[i].time;
    }

    // Approximate starting value for receiver clock
    t_pc = t_pc/chans + 75e-3;

    // Iterate to user xyzt solution using Taylor Series expansion:
  double err_mag;
    for(j=0; j<MAX_ITER; j++) {
        t_rx = t_pc - p->time;
        for (i=0; i<chans; i++) {
            // Convert SV position to ECI coords (20.3.3.4.3.3.2)
            double theta = (t_tx[i] - t_rx) * OMEGA_E;

            double x_sv_eci = x_sv[i]*cos(theta) - y_sv[i]*sin(theta);
            double y_sv_eci = x_sv[i]*sin(theta) + y_sv[i]*cos(theta);
            double z_sv_eci = z_sv[i];

            // Geometric range (20.3.3.4.3.4)
            double gr = sqrt(pow(p->x - x_sv_eci, 2) +
                             pow(p->y - y_sv_eci, 2) +
                             pow(p->z - z_sv_eci, 2));

            dPR[i] = SPEED_OF_LIGHT*(t_rx - t_tx[i]) - gr;

            jac[i][0] = (p->x - x_sv_eci) / gr;
            jac[i][1] = (p->y - y_sv_eci) / gr;
            jac[i][2] = (p->z - z_sv_eci) / gr;
            jac[i][3] = SPEED_OF_LIGHT;
        }

        // ma = transpose(H) * W * H
        for (r=0; r<4; r++)
            for (c=0; c<4; c++) {
            ma[r][c] = 0;
            for (i=0; i<chans; i++) ma[r][c] += jac[i][r]*weight[i]*jac[i][c];
        }

        double determinant =
            ma[0][3]*ma[1][2]*ma[2][1]*ma[3][0] - ma[0][2]*ma[1][3]*ma[2][1]*ma[3][0] - ma[0][3]*ma[1][1]*ma[2][2]*ma[3][0] + ma[0][1]*ma[1][3]*ma[2][2]*ma[3][0]+
            ma[0][2]*ma[1][1]*ma[2][3]*ma[3][0] - ma[0][1]*ma[1][2]*ma[2][3]*ma[3][0] - ma[0][3]*ma[1][2]*ma[2][0]*ma[3][1] + ma[0][2]*ma[1][3]*ma[2][0]*ma[3][1]+
            ma[0][3]*ma[1][0]*ma[2][2]*ma[3][1] - ma[0][0]*ma[1][3]*ma[2][2]*ma[3][1] - ma[0][2]*ma[1][0]*ma[2][3]*ma[3][1] + ma[0][0]*ma[1][2]*ma[2][3]*ma[3][1]+
            ma[0][3]*ma[1][1]*ma[2][0]*ma[3][2] - ma[0][1]*ma[1][3]*ma[2][0]*ma[3][2] - ma[0][3]*ma[1][0]*ma[2][1]*ma[3][2] + ma[0][0]*ma[1][3]*ma[2][1]*ma[3][2]+
            ma[0][1]*ma[1][0]*ma[2][3]*ma[3][2] - ma[0][0]*ma[1][1]*ma[2][3]*ma[3][2] - ma[0][2]*ma[1][1]*ma[2][0]*ma[3][3] + ma[0][1]*ma[1][2]*ma[2][0]*ma[3][3]+
            ma[0][2]*ma[1][0]*ma[2][1]*ma[3][3] - ma[0][0]*ma[1][2]*ma[2][1]*ma[3][3] - ma[0][1]*ma[1][0]*ma[2][2]*ma[3][3] + ma[0][0]*ma[1][1]*ma[2][2]*ma[3][3];

        // mb = inverse(ma) = inverse(transpose(H)*W*H)
        mb[0][0] = (ma[1][2]*ma[2][3]*ma[3][1] - ma[1][3]*ma[2][2]*ma[3][1] + ma[1][3]*ma[2][1]*ma[3][2] - ma[1][1]*ma[2][3]*ma[3][2] - ma[1][2]*ma[2][1]*ma[3][3] + ma[1][1]*ma[2][2]*ma[3][3]) / determinant;
        mb[0][1] = (ma[0][3]*ma[2][2]*ma[3][1] - ma[0][2]*ma[2][3]*ma[3][1] - ma[0][3]*ma[2][1]*ma[3][2] + ma[0][1]*ma[2][3]*ma[3][2] + ma[0][2]*ma[2][1]*ma[3][3] - ma[0][1]*ma[2][2]*ma[3][3]) / determinant;
        mb[0][2] = (ma[0][2]*ma[1][3]*ma[3][1] - ma[0][3]*ma[1][2]*ma[3][1] + ma[0][3]*ma[1][1]*ma[3][2] - ma[0][1]*ma[1][3]*ma[3][2] - ma[0][2]*ma[1][1]*ma[3][3] + ma[0][1]*ma[1][2]*ma[3][3]) / determinant;
        mb[0][3] = (ma[0][3]*ma[1][2]*ma[2][1] - ma[0][2]*ma[1][3]*ma[2][1] - ma[0][3]*ma[1][1]*ma[2][2] + ma[0][1]*ma[1][3]*ma[2][2] + ma[0][2]*ma[1][1]*ma[2][3] - ma[0][1]*ma[1][2]*ma[2][3]) / determinant;
        mb[1][0] = (ma[1][3]*ma[2][2]*ma[3][0] - ma[1][2]*ma[2][3]*ma[3][0] - ma[1][3]*ma[2][0]*ma[3][2] + ma[1][0]*ma[2][3]*ma[3][2] + ma[1][2]*ma[2][0]*ma[3][3] - ma[1][0]*ma[2][2]*ma[3][3]) / determinant;
        mb[1][1] = (ma[0][2]*ma[2][3]*ma[3][0] - ma[0][3]*ma[2][2]*ma[3][0] + ma[0][3]*ma[2][0]*ma[3][2] - ma[0][0]*ma[2][3]*ma[3][2] - ma[0][2]*ma[2][0]*ma[3][3] + ma[0][0]*ma[2][2]*ma[3][3]) / determinant;
        mb[1][2] = (ma[0][3]*ma[1][2]*ma[3][0] - ma[0][2]*ma[1][3]*ma[3][0] - ma[0][3]*ma[1][0]*ma[3][2] + ma[0][0]*ma[1][3]*ma[3][2] + ma[0][2]*ma[1][0]*ma[3][3] - ma[0][0]*ma[1][2]*ma[3][3]) / determinant;
        mb[1][3] = (ma[0][2]*ma[1][3]*ma[2][0] - ma[0][3]*ma[1][2]*ma[2][0] + ma[0][3]*ma[1][0]*ma[2][2] - ma[0][0]*ma[1][3]*ma[2][2] - ma[0][2]*ma[1][0]*ma[2][3] + ma[0][0]*ma[1][2]*ma[2][3]) / determinant;
        mb[2][0] = (ma[1][1]*ma[2][3]*ma[3][0] - ma[1][3]*ma[2][1]*ma[3][0] + ma[1][3]*ma[2][0]*ma[3][1] - ma[1][0]*ma[2][3]*ma[3][1] - ma[1][1]*ma[2][0]*ma[3][3] + ma[1][0]*ma[2][1]*ma[3][3]) / determinant;
        mb[2][1] = (ma[0][3]*ma[2][1]*ma[3][0] - ma[0][1]*ma[2][3]*ma[3][0] - ma[0][3]*ma[2][0]*ma[3][1] + ma[0][0]*ma[2][3]*ma[3][1] + ma[0][1]*ma[2][0]*ma[3][3] - ma[0][0]*ma[2][1]*ma[3][3]) / determinant;
        mb[2][2] = (ma[0][1]*ma[1][3]*ma[3][0] - ma[0][3]*ma[1][1]*ma[3][0] + ma[0][3]*ma[1][0]*ma[3][1] - ma[0][0]*ma[1][3]*ma[3][1] - ma[0][1]*ma[1][0]*ma[3][3] + ma[0][0]*ma[1][1]*ma[3][3]) / determinant;
        mb[2][3] = (ma[0][3]*ma[1][1]*ma[2][0] - ma[0][1]*ma[1][3]*ma[2][0] - ma[0][3]*ma[1][0]*ma[2][1] + ma[0][0]*ma[1][3]*ma[2][1] + ma[0][1]*ma[1][0]*ma[2][3] - ma[0][0]*ma[1][1]*ma[2][3]) / determinant;
        mb[3][0] = (ma[1][2]*ma[2][1]*ma[3][0] - ma[1][1]*ma[2][2]*ma[3][0] - ma[1][2]*ma[2][0]*ma[3][1] + ma[1][0]*ma[2][2]*ma[3][1] + ma[1][1]*ma[2][0]*ma[3][2] - ma[1][0]*ma[2][1]*ma[3][2]) / determinant;
        mb[3][1] = (ma[0][1]*ma[2][2]*ma[3][0] - ma[0][2]*ma[2][1]*ma[3][0] + ma[0][2]*ma[2][0]*ma[3][1] - ma[0][0]*ma[2][2]*ma[3][1] - ma[0][1]*ma[2][0]*ma[3][2] + ma[0][0]*ma[2][1]*ma[3][2]) / determinant;
        mb[3][2] = (ma[0][2]*ma[1][1]*ma[3][0] - ma[0][1]*ma[1][2]*ma[3][0] - ma[0][2]*ma[1][0]*ma[3][1] + ma[0][0]*ma[1][2]*ma[3][1] + ma[0][1]*ma[1][0]*ma[3][2] - ma[0][0]*ma[1][1]*ma[3][2]) / determinant;
        mb[3][3] = (ma[0][1]*ma[1][2]*ma[2][0] - ma[0][2]*ma[1][1]*ma[2][0] + ma[0][2]*ma[1][0]*ma[2][1] - ma[0][0]*ma[1][2]*ma[2][1] - ma[0][1]*ma[1][0]*ma[2][2] + ma[0][0]*ma[1][1]*ma[2][2]) / determinant;

        // mc = inverse(transpose(H)*W*H) * transpose(H)
        for (r=0; r<4; r++)
            for (c=0; c<chans; c++) {
            mc[r][c] = 0;
            for (i=0; i<4; i++) mc[r][c] += mb[r][i]*jac[c][i];
        }

        // md = inverse(transpose(H)*W*H) * transpose(H) * W * dPR
        for (r=0; r<4; r++) {
            md[r] = 0;
            for (i=0; i<chans; i++) md[r] += mc[r][i]*weight[i]*dPR[i];
        }

        double dx = md[0];
        double dy = md[1];
        double dz = md[2];
        double dt = md[3];

        err_mag = sqrt(dx*dx + dy*dy + dz*dz);


        if (err_mag<1.0) break;

        p->x    += dx;
        p->y    += dy;
        p->z    += dz;
        p->time += dt;
    }
    return j;
}

static void LatLonAlt(
    double x_n, double y_n, double z_n,
    double *lat, double *lon, double *alt) {
    int iterations = 100;
    const double a  = WGS84_A;
    const double e2 = WGS84_E2;

    const double p = sqrt(x_n*x_n + y_n*y_n);

    *lon = 2.0 * atan2(y_n, x_n + p);
    *lat = atan(z_n / (p * (1.0 - e2)));
    *alt = 0.0;

    while(iterations > 0) {
        double tmp = *alt;
        double N = a / sqrt(1.0 - e2*pow(sin(*lat),2));
        *alt = p/cos(*lat) - N;
        *lat = atan(z_n / (p * (1.0 - e2*N/(N + *alt))));
        if(fabs(*alt-tmp)<1e-3) 
            break;
        iterations--;
    }
}

static void attempt_solution(struct Snapshot *s) 
{
    int sv_count = 0;
    int sv_ids[N_SV];
    int i;
    struct Location predicted_location;
    struct Location *sv_location;
    double lat,lon,alt;
    int q, valid_locations;
  
    /* First, filter out who we can use in the solution */
    for(i = 0; i < MAX_SV; i++) {
        int id, j;
        /* Find a valid entry in the snapshot */
        if(!(s->entries[i].state & SNAPSHOT_STATE_LOCKED) )      continue;
        if(!(s->entries[i].state & SNAPSHOT_STATE_ORBIT_VALID) ) continue;
        if(!(s->entries[i].state & SNAPSHOT_STATE_TIME_VALID) )  continue;        
        id = s->entries[i].id;
        
        /* Check we can find the matching entry in the Space_vehicle table */
        for(j = 0 ; j < N_SV; j++) {
            if(space_vehicles[j].id == id)
                break;
        }
        /* If not found */
        if(j == N_SV) continue;
        
        /* Yes, we will use this ID */
        sv_ids[sv_count] = id;
        sv_count++;
    }

    /* Not enough vaild data to find the location! */
    if(sv_count < 4) {
        return;
    }
  
    /* Allocate space to hold the space vehicle locations */
    sv_location = malloc(sizeof (struct Location)*sv_count);
    if(sv_location == NULL) {
        printf("Out of memory \n");
        return;
    }
  
    /* Calculate the Space Vehicle positions at time of transmit */
    valid_locations = 0;
    for(q = 0; q < sv_count; q++) {
        int e, sv;
        
        unsigned phase_in_gold_code;  /* value is 0 to (1023*64-1) */
        /* Find the Snapshot entry for this ID */
        for(e = 0; e < MAX_SV; e++) {
            if(s->entries[e].id == sv_ids[q])
                break;
        }
        if(e == MAX_SV) {
            printf("UNEXPECTED! Unable to find snapshot entry for id %02i!\n",sv_ids[q]);
            continue;
        }

        /* Find the Space Vehicle entry for this ID */
        for(sv = 0; sv < N_SV; sv++) {
            if(space_vehicles[sv].id == sv_ids[q])
                break;
        }
        if(sv == N_SV) {
            printf("UNEXPECTED! Unable to find Space Vehicle entry!\n");
            continue;
        }
        
        phase_in_gold_code    = (s->entries[e].lock_code_nco >> 1) & 0x7FFFFFFF;
    
        /* calc transmit time milliseconds  */
        space_vehicles[sv].time_raw   = s->entries[e].nav_subframe_of_week * 6000 + s->entries[e].lock_ms_of_frame
                                      + ((double)phase_in_gold_code)/(1023*(1<<21));
        /* Convert from milliseconds to seconds */
        space_vehicles[sv].time_raw  /= 1000.0;                                    
        
        /* Correct the time using calibration factors */ 
        space_vehicles[sv].pos_t_valid  = 0;
        sv_calc_corrected_time(sv);
        /* calculate the location of the space vehicle */
        sv_calc_location(sv, sv_location+valid_locations);
        
        /* Verify that the location is valid */
        if(sv_location[valid_locations].x < 40000000 && sv_location[valid_locations].x > -40000000) 
            if(sv_location[valid_locations].y < 40000000 && sv_location[valid_locations].y > -40000000)
                if(sv_location[valid_locations].z < 40000000 && sv_location[valid_locations].z > -40000000)
                    valid_locations++;
    }

#if 1
    for(q = 0; q < valid_locations; q++) {
        printf("Location is (%16.5f, %16.5f, %16.5f) @ %15.8f\n", sv_location[q].x, sv_location[q].y, sv_location[q].z, sv_location[q].time);
    }
#endif
  
    if(valid_locations < 4) {
        free(sv_location);
        return;
    }

    A_solve(valid_locations, sv_location, &predicted_location);
#if 1
    printf("\nSolved is  (%20f, %20f, %20f) @ %20f (alt %20f)\n", 
        predicted_location.x, predicted_location.y, predicted_location.z, predicted_location.time,
        sqrt(predicted_location.x*predicted_location.x
           + predicted_location.y*predicted_location.y
           + predicted_location.z*predicted_location.z));
#endif        
    LatLonAlt(predicted_location.x, predicted_location.y, predicted_location.z, &lat, &lon, &alt);
    printf("Lat/Lon/Alt : %20.6f, %20.6f, %20.1f\n", lat*180/PI, lon*180/PI, alt);

    if(position_file != NULL) {
        fprintf(position_file,"%16.5f, %16.5f, %16.5f, %15.8f,  %20.6f, %20.6f, %20.1f\n", 
                              predicted_location.x, predicted_location.y, predicted_location.z, predicted_location.time,
                              lat*180/PI, lon*180/PI, alt);
    }

    free(sv_location);
    return;
}