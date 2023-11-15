#include "track.h"


static void start_acquire(struct Space_vehicle *sv) 
{

            sv->state = state_acquiring;
            sv->acquire.max_power = 0;
}


void track_update(struct Space_vehicle *sv) 
{
    /**********************************************************
    * We have enough power to see if we can work toward locking
    **********************************************************/
    if(sv->track.max_power < track_unlock_power) {
        sv->track.percent_locked--;
        if(sv->track.percent_locked==0) {
            start_acquire(sv);
#if SHOW_LOCK_UNLOCK         
            printf("Unlocked %i\n", sv->id);
#endif
            sv->state = state_acquiring;
            sv->acquire.max_power = 0;
        }
    } else {
        /***************************************
        * If this is  is the local maximum, then
        * se can moved towards being locked 
        ***************************************/
        if(sv->track.power[1][1] >= sv->track.power[1][0] &&
           sv->track.power[1][1] >= sv->track.power[1][2] &&
           sv->track.power[1][1] >= sv->track.power[0][1] &&
           sv->track.power[1][1] >= sv->track.power[2][1]) {
           sv->track.percent_locked+=5;
        }

        if(sv->track.percent_locked > 99) {
            sv->track.percent_locked = 100;  
            start_locked(sv, 2);  // Offset of two from peak power
        } else {
            sv->track.max_power = 0;
            sv->track.band   = sv->track.max_band;
            sv->track.offset = sv->track.max_offset;
        }
    }
}


void track(struct Space_vehicle *sv) 
{
    int line,i;
    if((sv->track.offset+1)%samples_per_ms == code_offset_in_ms) {
        line =0;
    } else if(sv->track.offset == code_offset_in_ms) {
        line = 1;
    } else if((sv->track.offset+samples_per_ms-1)%samples_per_ms == code_offset_in_ms) {
        line = 2;
    } else if((sv->track.offset+samples_per_ms-2)%samples_per_ms == code_offset_in_ms) {
        track_update(sv);
        return;
    } else {
        return;
    }

#if PRINT_TRACK_POWER
    if(line == 0) printf("\n");
    printf("%2i %2i%% %5i: ", sv->id, sv->track.percent_locked, code_offset_in_ms);
    for(i = 0; i < sv->track.band-1;i++)
            printf("      ");      
#endif
    for(i = 0; i <3; i++) {
        int band;
        int sin_power, cos_power, power;

        band = sv->track.band-1+i;
        if(band < 0) band = 0;
        if(band >= search_bands) band = search_bands-1;

        xor_to_work(work_buffer, sample_history, sv->acquire.seek_in_phase[band]);
        sin_power = count_one_bits(work_buffer, samples_for_acquire) - samples_for_acquire/2;

        xor_to_work(work_buffer, sample_history, sv->acquire.seek_quadrature[band]);
        cos_power = count_one_bits(work_buffer, samples_for_acquire) - samples_for_acquire/2;

        power = sin_power*sin_power + cos_power*cos_power;
        sv->track.power[line][i] = power;
#if PRINT_TRACK_POWER
        if(power > PRINT_TRACK_SQUETCH) 
            printf("%5i ", sv->track.power[line][i]/1000);
        else
            printf("      ");      
#endif
        if(power > sv->track.max_power) {
            sv->track.max_power  = power;
            sv->track.max_band   = band;
            sv->track.max_offset = code_offset_in_ms;
        }
    }
#if PRINT_TRACK_POWER
    printf("\n");      
#endif

    /************************************************************
    * If we aren't on the last of the three lines, then return
    ************************************************************/
    if(line != 2) 
        return;
    
}


