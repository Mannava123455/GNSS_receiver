static void start_tracking(struct Space_vehicle *sv)
 {
    sv->state          = state_tracking;
    sv->track.percent_locked = 50;

    /* Where we are hunting around */
    sv->track.band       = sv->acquire.max_band;
    sv->track.offset     = sv->acquire.max_offset;

    sv->track.max_power  = 0;           
}

static void acquire(struct Space_vehicle *sv) 
{
   int band;

   for(band = 0; band < search_bands; band++) 
   {
      int sin_power, cos_power, power;
      xor_to_work(work_buffer, sample_history, sv->acquire.seek_in_phase[band]);
      sin_power = count_one_bits(work_buffer, samples_for_acquire) - samples_for_acquire/2;

      xor_to_work(work_buffer, sample_history, sv->acquire.seek_quadrature[band]);
      cos_power = count_one_bits(work_buffer, samples_for_acquire) - samples_for_acquire/2;

      power = sin_power*sin_power + cos_power*cos_power;
#if PRINT_ACQUIRE_POWERS
      if(power > PRINT_ACQUIRE_SQUETCH) 
         printf("%5i ", power/1000);
      else
         printf("      ");
      
#endif
      if(sv->acquire.max_power < power) {
        sv->acquire.max_power  = power;
        sv->acquire.max_band   = band;
        sv->acquire.max_offset = code_offset_in_ms;
      }
   }
#if PRINT_ACQUIRE_POWERS
   printf("\n");
#endif
   if(code_offset_in_ms  == 0) {
       if(sv->acquire.max_power > acquire_min_power) {
           start_tracking(sv);

       } else {
          sv->acquire.max_power = 0;           
       }
       /*printf("%02i: Max power %7i at band %2i, offset %5i %s\n", 
              sv->id,
            sv->acquire.max_power,
            sv->acquire.max_band,
            sv->acquire.max_offset,
            sv->state == state_tracking ? "TRACKING" : ""); */      
   }
}