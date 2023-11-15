#include "setup.h"
#include "gold_codes.h"
#include "acquire.h"
#include "track.h"
#include "solve.h"




static void gps_process_sample(int s) 
{
  int sv;
  static int prime = 0;
  static int processed = 0;
  add_to_bitmap(sample_history,s);
  if(prime < samples_for_acquire) {
     if(prime == 0) {
       printf("Starting to prime sample history\n");
     }
     prime++;
     if(prime == samples_for_acquire) {
       printf("History primed with %i samples (%i milliseconds of data)\n", samples_for_acquire, ms_for_acquire);
     }
     return;
  }


  for(sv = 0; sv < N_SV; sv++) {
    int prompt_code_index, prompt_code_index_next_cycle;
    switch(space_vehicles[sv].state) {
       case state_acquiring:
            if(processed < samples_per_ms+100)
                acquire(space_vehicles+sv);
            break;
       case state_tracking:
            track(space_vehicles+sv);
            break;
       case state_locked:
            prompt_code_index            = space_vehicles[sv].lock.code_nco>>22;
            prompt_code_index_next_cycle = (space_vehicles[sv].lock.code_nco + space_vehicles[sv].lock.code_nco_step)>>22;

            accumulate(space_vehicles+sv, s);

           
            if(prompt_code_index != prompt_code_index_next_cycle) {

              if(prompt_code_index == CHIPS_PER_MS-2) 
                 update_early(space_vehicles+sv, prompt_code_index, prompt_code_index_next_cycle);

              if(prompt_code_index == CHIPS_PER_MS-1) 
                update_prompt(space_vehicles+sv,  prompt_code_index, prompt_code_index_next_cycle);

              if(prompt_code_index == 0) 
                 update_late(space_vehicles+sv, prompt_code_index, prompt_code_index_next_cycle);

              if(prompt_code_index == 1)
                adjust_early_late(space_vehicles+sv);
            }
            update_ncos(space_vehicles+sv);
            break;
       default:
            space_vehicles[sv].state = state_acquiring;
            break;
    }
  }
  if(code_offset_in_ms>0)
     code_offset_in_ms--;
  else
     code_offset_in_ms = samples_per_ms-1;
  processed++;

#if PRINT_SAMPLE_NUMBERS
  if(processed % PRINT_SAMPLE_FREQUENCY == 0) 
     {
        int i, locked = 0;
        for(i = 0; i < N_SV; i++)
            if(space_vehicles[i].state == state_locked)

                locked++;
        printf("Processing sample %i,   %i locked\n",processed);
     }
 #endif
#if PRINT_LOCKED_NCO_VALUES

  if(processed % samples_per_ms == 0) 
    {
    int i;
    for(i = 0; i < N_SV; i++)
        printf("%4i.%06i ",space_vehicles[i].lock_code_nco>>22, (space_vehicles[i].lock_code_nco>>16 & 0x3f)* 15625);
    putchar('\n');
    }
#endif
 
 if(processed % (samples_per_ms*SHOW_SOLUTION_MS) == 0)
  {
     struct Snapshot s;
     snapshot_timing(&s);
     attempt_solution(&s);
 } else if(processed % (samples_per_ms*SHOW_TIMING_SNAPSHOT_FREQ_MS) == 0) 
 {
     struct Snapshot s;

     snapshot_timing(&s);
 }
}