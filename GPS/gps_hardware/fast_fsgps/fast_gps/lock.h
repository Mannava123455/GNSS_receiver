#include "nav.h"


static void start_locked(struct Space_vehicle *sv, int offset_from_peak) {
    int lower_delta=0, upper_delta=0;
    int start_freq, fine_adjustment;
    long long step;

    start_freq = (int)band_bandwidth * ((int)sv->track.band-(search_bands/2));
    lower_delta = (sv->track.power[1][1] - sv->track.power[1][0])/1024;
    upper_delta = (sv->track.power[1][1] - sv->track.power[1][2])/1024;

    /* Clamp to prevent divide by zero */
    if(lower_delta < 1) lower_delta = 1;
    if(upper_delta < 1) upper_delta = 1;

    if(lower_delta > upper_delta) {
      fine_adjustment = (int)band_bandwidth * (lower_delta-upper_delta) / lower_delta;
    } else if(lower_delta < upper_delta) {
      fine_adjustment = - (int)band_bandwidth * (lower_delta-upper_delta) / upper_delta;
    } else {
      fine_adjustment = 0;
    }
    printf("Adjust %4i   \n",fine_adjustment);
    start_freq -= fine_adjustment;


    sv->state = state_locked;
    sv->nav_time.time_good = 0;
    
    /* Prime the IIR filter so we don't unlock immediately */
    sv->lock.filtered_power = 1000000;

    /* Set up the NCO parameters */

    step = ((1<<30) / (samples_per_ms * 1000/4) * start_freq)  + (unsigned)((long long)(1<<30)*4*if_cycles_per_ms/samples_per_ms);
    sv->lock.phase_nco_sine       = 0;
    sv->lock.phase_nco_cosine     = 0x40000000;
    sv->lock.phase_nco_step       = step;

    sv->lock.code_nco_step          = (unsigned)((long long)(1<<22)*1023/samples_per_ms);
    sv->lock.code_nco_filter      = 0;
    sv->lock.code_nco = offset_from_peak * sv->lock.code_nco_step;
    sv->lock.code_nco_trend = start_freq*272/100;
#if 0
    int s,c;
    /*** This doesn't work *****/
    /* Set up the last angle, preventing any initial angle from
       upsetting the ability lock */
    s = sv->lock.prompt_sine_total;
    c = sv->lock.prompt_cosine_total;    
    while(c > 15 || c < -15 || s > 15 || s < -15) {
        c /= 2;
        s /= 2;
    }
    s &= ATAN2_SIZE-1;  c &= ATAN2_SIZE-1;
    sv->lock.last_angle = atan2_lookup[c][s];
#endif
    sv->lock.last_angle = 0;

    /* Reset the running totals */
    sv->lock.early_sine_count_last    = sv->lock.early_sine_count; 
    sv->lock.early_cosine_count_last  = sv->lock.early_cosine_count;
    sv->lock.prompt_sine_count_last   = sv->lock.prompt_sine_count; 
    sv->lock.prompt_cosine_count_last = sv->lock.prompt_cosine_count;
    sv->lock.late_sine_count_last     = sv->lock.late_sine_count; 
    sv->lock.late_cosine_count_last   = sv->lock.late_cosine_count;

    sv->lock.early_power           = 0;
    sv->lock.early_power_not_reset = 0;
    sv->lock.prompt_power          = 2 * lock_lost_power;
    sv->lock.late_power            = 0;
    sv->lock.late_power_not_reset  = 0;
    sv->lock.delta_filtered        = 0;
    sv->lock.angle_filtered        = 0;
    sv->lock.ms_of_bit             = 0;
    sv->navdata.bit_errors         = 0;
    
#if LOCK_SHOW_INITIAL
    printf("%2i: ", sv->id);
    printf("Lower band %7i upper band %7i ", lower_delta, upper_delta);
    printf("Adjust %4i   ",fine_adjustment);
    printf("Freq guess %i\n",start_freq);
    printf("\nLock band %i, Lock offset %i, step %x,  Code NCO %8x\n", sv->track.band, sv->track.offset, (unsigned) step, sv->lock.code_nco>>22);
    printf("lock_phase_nco_step  %8x\n",sv->lock.phase_nco_step);
    printf("lock code_nco & step    %8x   %8x %i\n",sv->lock.code_nco, sv->lock.code_nco_step, sv->lock.code_nco_trend);
#endif

#if WRITE_BITS
    char name[100];
    sprintf(name,"bits.%i",sv->id);
    sv->bits_file = fopen(name,"wb");
    if(sv->bits_file == NULL) {
        printf("WARNING : UNABLE TO OPEN '%s'\n",name);
    }
#else    
    sv->bits_file = NULL;
#endif
}



static void accumulate(struct Space_vehicle *sv, int sample) 
{
    int early_code_index,  late_code_index;
    uint_8 sine_positive, cosine_positive;
    int prompt_code_index;

    prompt_code_index            = sv->lock.code_nco>>22;

    early_code_index  = (prompt_code_index == CHIPS_PER_MS-1) ? 0: prompt_code_index+1;
    late_code_index   = (prompt_code_index == 0) ? CHIPS_PER_MS-1: prompt_code_index-1;

    /***********************************************************
    * What is our current sein()/cosine() (I/Q) value?
    ***********************************************************/
    sine_positive   = (sv->lock.phase_nco_sine   & 0x80000000) ? 0 : 1;
    cosine_positive = (sv->lock.phase_nco_cosine & 0x80000000) ? 0 : 1;

    if(sv->gold_code[early_code_index] ^ sample) {
        sv->lock.early_sine_count    += sine_positive;
        sv->lock.early_cosine_count  += cosine_positive;
    }

    if(sv->gold_code[prompt_code_index] ^ sample) {
        sv->lock.prompt_sine_count   += sine_positive;
        sv->lock.prompt_cosine_count += cosine_positive;
    }

    if(sv->gold_code[late_code_index] ^ sample) {
        sv->lock.late_sine_count     += sine_positive;
        sv->lock.late_cosine_count   += cosine_positive;
    }
}

static void update_early(struct Space_vehicle *sv, int prompt_code_index, int prompt_code_index_next_cycle)
 {

#if DOUBLECHECK_PROMPT_CODE_INDEX
    int early_code_index;

    early_code_index  = (prompt_code_index == CHIPS_PER_MS-1) ? 0: prompt_code_index+1;

    /* This should never be true, but just in case... */
    if(prompt_code_index == prompt_code_index_next_cycle) {
        printf("Bad prompt_code_index in update_early()\n");
        return;
    }
    

    /***********************************************************
    * Ensure that this is the last data bitt for this repeat of 
    * the prompt C/A code?
    ***********************************************************/
    if(early_code_index != CHIPS_PER_MS-1) {
       printf("Bad prompt_code_index in update_early()\n");
       return;
    }
#endif

    /* Work out the changes over the last repeat of the Gold code */
    sv->lock.early_sine   = sv->lock.early_sine_count   - sv->lock.early_sine_count_last   - samples_per_ms/4;
    sv->lock.early_cosine = sv->lock.early_cosine_count - sv->lock.early_cosine_count_last - samples_per_ms/4;
    sv->lock.early_sine_count_last   = sv->lock.early_sine_count;
    sv->lock.early_cosine_count_last = sv->lock.early_cosine_count;

    sv->lock.early_power -= sv->lock.early_power/LATE_EARLY_IIR_FACTOR;
    sv->lock.early_power += sv->lock.early_sine   * sv->lock.early_sine
                          + sv->lock.early_cosine * sv->lock.early_cosine;
                             
    sv->lock.early_power_not_reset -= sv->lock.early_power_not_reset/LATE_EARLY_IIR_FACTOR;
    sv->lock.early_power_not_reset += sv->lock.early_sine   * sv->lock.early_sine
                                    + sv->lock.early_cosine * sv->lock.early_cosine;
}




static void adjust_prompt(struct Space_vehicle *sv) 
{
    int s, c;
    int_8 delta;
    int adjust = 0;
    uint_8 angle;
    uint_8 this_bit;

    s = sv->lock.prompt_sine;
    c = sv->lock.prompt_cosine;
    while(c > 15 || c < -15 || s > 15 || s < -15) {
        c /= 2;
        s /= 2;
    }

    s &= ATAN2_SIZE-1;  c &= ATAN2_SIZE-1;
    angle = atan2_lookup[c][s];

    delta = angle - sv->lock.last_angle;
    sv->lock.last_angle = angle;
 
   sv->lock.delta_filtered -= sv->lock.delta_filtered / LOCK_DELTA_IIR_FACTOR;
    sv->lock.delta_filtered += delta;

    adjust = angle;
    sv->lock.angle_filtered -= sv->lock.angle_filtered / LOCK_ANGLE_IIR_FACTOR;
    sv->lock.angle_filtered += angle;

    if(angle >=128)
        sv->lock.angle_filtered -= 256;

    adjust = sv->lock.angle_filtered/8;
    
    adjust  += (1<<24) / 32 / LOCK_DELTA_IIR_FACTOR / samples_per_ms * sv->lock.delta_filtered;
    sv->lock.phase_nco_step  -= adjust;
#if LOCK_SHOW_ANGLES
    printf("%6i, %6i, %3i,%4i,%6i, %6i, %6i\n",sv->lock.prompt_sine_power, sv->lock.prompt_cosine_power, angle,delta, sv->lock.delta_filtered, adjust, sv->lock.phase_nco_step);
#endif    
  
    if(sv->lock.prompt_cosine < 0)
        this_bit = 0;
    else
        this_bit = 1;
    sv->lock.ms_of_bit++;
    if(sv->lock.ms_of_bit == MS_PER_BIT || sv->lock.last_bit != this_bit)
        sv->lock.ms_of_bit = 0;
    sv->lock.last_bit = this_bit;

    if(sv->lock.ms_of_frame == MS_PER_BIT*BITS_PER_FRAME-1) {
        sv->lock.ms_of_frame = 0;
        if(sv->navdata.subframe_of_week == 7*24*60*60/6-1) {
            sv->navdata.subframe_of_week=0;
        } else {
            sv->navdata.subframe_of_week++;
        }
    } else {
        sv->lock.ms_of_frame++;
    }
  
    nav_process(sv,this_bit);

#if LOCK_SHOW_BITS
    if(sv->lock_ms_of_bit == 0)
        putchar('\n');
    putchar('0'+this_bit);

#endif

#if LOCK_SHOW_BPSK_PHASE_PER_MS
    if(sv->bits_file) {
        if(sv->lock_ms_of_bit == 0)
            putc('\n',sv->bits_file);
        putc('0'+this_bit,sv->bits_file);
    }
#endif
 
}


static void update_prompt(struct Space_vehicle *sv, int prompt_code_index, int prompt_code_index_next_cycle) 
{
#if DOUBLECHECK_PROMPT_CODE_INDEX
    /*************************************************
    * This should never be true, but just in case... 
    *************************************************/
    if(prompt_code_index == prompt_code_index_next_cycle) {
        printf("Bad prompt_code_index in update_prompt()\n");
        return;
    }
    
    /***********************************************************
    * Make sure that this is the last data bit for this 
    * repeat of the prompt C/A code?
    ***********************************************************/
    /* This too should never be true, but just in case... */
    if(prompt_code_index != CHIPS_PER_MS-1) {
        printf("Bad prompt_code_index in update_prompt()\n");
        return;
    }
#endif

    /***********************
    * Yes - so do the update 
    ***********************/
    sv->lock.prompt_sine   = sv->lock.prompt_sine_count   - sv->lock.prompt_sine_count_last    - samples_per_ms/4;
    sv->lock.prompt_cosine = sv->lock.prompt_cosine_count - sv->lock.prompt_cosine_count_last  - samples_per_ms/4;
    sv->lock.prompt_sine_count_last = sv->lock.prompt_sine_count;
    sv->lock.prompt_cosine_count_last = sv->lock.prompt_cosine_count;
    
    sv->lock.prompt_power -= sv->lock.prompt_power/LATE_EARLY_IIR_FACTOR;
    sv->lock.prompt_power += sv->lock.prompt_sine   * sv->lock.prompt_sine
                           + sv->lock.prompt_cosine * sv->lock.prompt_cosine;

#if LOCK_SHOW_PER_MS_IQ
    printf("%2i-%4i:  (%6i, %6i)   %8i\n", sv->id, sv->lock.code_nco>>22, 
    sv->lock.prompt_sine, sv->lock.prompt_cosine, sv->lock.prompt_power);
#endif        

    if(sv->lock.prompt_power/LATE_EARLY_IIR_FACTOR < lock_lost_power) { 
        printf("Lock lost at power %u", sv->lock.prompt_power/LATE_EARLY_IIR_FACTOR);

        sv->state = state_acquiring;
        return;
    }
    adjust_prompt(sv);
}


static void update_late(struct Space_vehicle *sv, int prompt_code_index, int prompt_code_index_next_cycle)
 {

#if DOUBLECHECK_PROMPT_CODE_INDEX
    int late_code_index;
    late_code_index   = (prompt_code_index == 0) ? CHIPS_PER_MS-1: prompt_code_index-1;

    /* This should never be true, but just in case... */
    if(prompt_code_index == prompt_code_index_next_cycle) {
        printf("Bad prompt_code_index in update_late()\n");
        return;
    }
    

    /***********************************************************
    * Is this the last data bit for this repeat of the prompt C/A code?
    ***********************************************************/
    if(late_code_index != CHIPS_PER_MS-1) {
        printf("Bad prompt_code_index in update_late()\n");
        return;
    }
#endif


    sv->lock.late_sine   = sv->lock.late_sine_count   - sv->lock.late_sine_count_last   - samples_per_ms/4;
    sv->lock.late_cosine = sv->lock.late_cosine_count - sv->lock.late_cosine_count_last - samples_per_ms/4;
    sv->lock.late_sine_count_last   = sv->lock.late_sine_count;
    sv->lock.late_cosine_count_last = sv->lock.late_cosine_count;

    sv->lock.late_power -= sv->lock.late_power/LATE_EARLY_IIR_FACTOR;
        
    sv->lock.late_power += sv->lock.late_sine   * sv->lock.late_sine
                         + sv->lock.late_cosine * sv->lock.late_cosine;
                            
    sv->lock.late_power_not_reset -= sv->lock.late_power_not_reset/LATE_EARLY_IIR_FACTOR;        
    sv->lock.late_power_not_reset += sv->lock.late_sine   * sv->lock.late_sine
                                   + sv->lock.late_cosine * sv->lock.late_cosine;
                            
#if LOCK_SHOW_PER_MS_POWER
    printf("%2i: %6i, %6i, %6i\n", sv->id,
    sv->lock.early_power_not_reset/LATE_EARLY_IIR_FACTOR,
    sv->lock.prompt_power,
    sv->lock.late_power_not_reset/LATE_EARLY_IIR_FACTOR);
#endif
}

static void adjust_early_late(struct Space_vehicle *sv) 
{
    int adjust;
    /* Use the relative power levels of the late and early codes 
     * to adjust the code NCO phasing */
    adjust =  sv->lock.code_nco_trend;

    if(sv->lock.early_power/5 > sv->lock.late_power/4) {
        sv->lock.late_power = (sv->lock.early_power*7+sv->lock.late_power)/8;
        adjust += samples_per_ms*1;
        sv->lock.code_nco_trend+=4;
    } else if(sv->lock.late_power/5 > sv->lock.early_power/4) {
        sv->lock.early_power = (sv->lock.late_power*7+sv->lock.early_power)/8;
        adjust  -= samples_per_ms*1;
        sv->lock.code_nco_trend-=4;
    }

    if(adjust < 0) {
        if( sv->lock.code_nco  < -adjust) 
            sv->lock.code_nco += 1023<<22;
    }
    sv->lock.code_nco += adjust;

    if(sv->lock.code_nco+adjust >= 1023<<22) 
        sv->lock.code_nco -= 1023<<22;
        
#if LOCK_SHOW_EARLY_LATE_TREND
    printf("%2i: %6i, %6i, %6i, %5i\n", sv->id,
    sv->lock.early_power_not_reset/LATE_EARLY_IIR_FACTOR,
    sv->lock.prompt_power,
    sv->lock.late_power_not_reset/LATE_EARLY_IIR_FACTOR,
    sv->lock.code_nco_trend);
#endif
}

static void update_ncos(struct Space_vehicle *sv) {    
    /***************************
    * Update the phase NCO 
    ***************************/
    sv->lock.phase_nco_sine   += sv->lock.phase_nco_step;
    sv->lock.phase_nco_cosine += sv->lock.phase_nco_step;
    /***********************************
    * Update the current C/A code offset
    ***********************************/
    sv->lock.code_nco += sv->lock.code_nco_step;
    if(sv->lock.code_nco >= CHIPS_PER_MS<<22)
        sv->lock.code_nco -= CHIPS_PER_MS<<22;
}

