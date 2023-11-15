
#include "gold_codes.h"


void generate_atan2_table(void) 
{
    int x,y;
    printf("Generating ATAN2 table\n");
    for(x = 0; x < ATAN2_SIZE; x++) {
        for(y = 0; y < ATAN2_SIZE; y++) {
            atan2_lookup[y][x] = 0;
        }
    }
    
    for(x = -(ATAN2_SIZE-1)/2; x <=ATAN2_SIZE/2-1; x++) {
        for(y = -(ATAN2_SIZE-1)/2; y <= ATAN2_SIZE/2-1; y++) {
            double a = atan2(x,y);
            a *= 256.0 / 3.141592;
            a += 0.5;
            if(a < 0) 
                a +=256;
            atan2_lookup[y&(ATAN2_SIZE-1)][x&(ATAN2_SIZE-1)] = a;
        }
    }
#if PRINT_ATAN2_TABLE
    for(x = 0; x < ATAN2_SIZE; x++) {
        for(y = 0; y < ATAN2_SIZE; y++) {
            printf("%5i,", atan2_lookup[y][x]);
        }
        putchar('\n');
    }
#endif    
}


static int count_one_bits(uint_32 *a, int i) {
  int count = 0;
  int j;
  uint_8 *b = (uint_8 *)a;

  static int one_bits[256];
  static int setup = 1;
  
  if(setup) {
      for(j = 0; j < 256; j++) {
          one_bits[j] = 0;
          if(j&0x01) one_bits[j]++;
          if(j&0x02) one_bits[j]++;
          if(j&0x04) one_bits[j]++;
          if(j&0x08) one_bits[j]++;
          if(j&0x10) one_bits[j]++;
          if(j&0x20) one_bits[j]++;
          if(j&0x40) one_bits[j]++;
          if(j&0x80) one_bits[j]++;
      }
      setup = 0;
  }

  count = 0;
  while(i >= 8) {
     count += one_bits[b[0]&0xFF];
     i -= 8;
     b++;
  }

  for(j = 0; j < i; j++) {
     if(b[0] & (1<<j))
         count++;
  }
  return count;
}

static void g1_lfsr(unsigned char *out) {
  int state = 0x3FF,i;
  for(i = 0; i < 1023; i++) {
    int new_bit;
    out[i]   = (state >>9) & 0x1;
    /* Update the G1 LFSR */
    new_bit = ((state >>9) ^ (state >>2))&1;
    state   = ((state << 1) | new_bit) & 0x3FF;
  }
}

/**********************************************************************
* Generate the G2 LFSR bit stream. Different satellites have different
* taps, which effectively alters the relative phase of G1 vs G2 codes
**********************************************************************/
static void g2_lfsr(unsigned char tap0, unsigned char tap1, unsigned char *out) {
  int state = 0x3FF,i;
  /* Adjust tap number from 1-10 to 0-9 */
  tap0--;
  tap1--;
  for(i = 0; i < 1023; i++) {
    int new_bit;

    out[i] = ((state >> tap0) ^ (state >> tap1)) & 0x1;


    /* Update the G2 LFSR  */
    new_bit = ((state >>9) ^ (state >>8) ^
               (state >>7) ^ (state >>5) ^
               (state >>2) ^ (state >>1))&1;
    state = ((state << 1) | new_bit) & 0x3FF;
  }
}

/**********************************************************************
* Combine the G1 and G2 codes to make each satellites code
**********************************************************************/
static void combine_g1_and_g2(unsigned char *g1, unsigned char *g2, unsigned char *out)
{
  int i;
  for(i = 0; i < 1023; i++ ) {
    out[i] = g1[i] ^ g2[i];
  }
}

/*********************************************************************
* Build the Gold codes for each Satellite from the G1 and G2 streams
*********************************************************************/
void generateGoldCodes(void)
{
  static unsigned char g1[1023];
  static unsigned char g2[32][1023];
  int sv;
  g1_lfsr(g1);
  
  for(sv = 0; sv < N_SV; sv++)
  {
    int i;

   // printf("Calculating Gold Code for SV %i\n",space_vehicles[sv].id);
    g2_lfsr(space_vehicles[sv].tap1, space_vehicles[sv].tap2, g2[sv]);
    combine_g1_and_g2(g1, g2[sv], space_vehicles[sv].gold_code);
    /*for(i = 0; i < 1023; i++) {
      if(space_vehicles[sv].gold_code[i])
        printf("1, ");
      else
        printf("0, ");
      if(i%31 == 30)
       printf("\n");
    } */
  }
}

static void add_to_bitmap(uint_32 *bitmap, int s) 
{
  int i;
  for(i = samples_for_acquire/32; i > 0; i--) {
     bitmap[i] <<= 1;
     if(bitmap[i-1]&0x80000000)
        bitmap[i]++;
  }
  /*************************
  * And now the last sample 
  *************************/
  bitmap[i] <<= 1;
  if(s)
     bitmap[i]++;
}

/*********************************************************************
* Set a bit in the bitmap 
*********************************************************************/
static void bitmap_set_bit(uint_32 *bitmap, int o, int s) 
{
 if(s) {
    bitmap[o/32] |= 1<<(o%32);
 } else {
    bitmap[o/32] &= ~(1<<(o%32));      
 }
}
static void xor_to_work(uint_32 *dest, uint_32 *a, uint_32 *b) 
{
  int i;
  for(i = 0; i < acquire_bitmap_size_u32; i++) {
     dest[i] = a[i] ^ b[i];
  }
}
/********************************************
* Stretch the C/A code out to the required 
* of bits to cover the acquision test 
********************************************/
static void stretchGoldCodes(void) {
  int i;
  for(i = 0; i < N_SV; i++) 
  {
    int j;
    for(j = 0; j < samples_for_acquire; j++)
    {
       int index = (j*1023/samples_per_ms)%1023;
       bitmap_set_bit(space_vehicles[i].acquire.gold_code_stretched, 
                      samples_for_acquire-1 - j,
                      space_vehicles[i].gold_code[index]);
    }
  }
}


/********************************************
* Mix the G/A codes with the different LO
* freqencies, to give the final bitmap used
* to humt for the space vehicles
*******************************************/
static void mixLocalOscAndGoldCodes(unsigned sample_freq, unsigned if_freq) {
  int band;
  sample_freq /= 1000;
  if_freq     /= 1000;
  for(band = 0; band < search_bands; band++) {        
    int i, p, s;
    /************************************
    * Step for phase accumulator for this 
    * band
    ************************************/
    s = samples_for_acquire*if_freq/sample_freq + band - search_bands/2;
    /**********************************
    * Calculate IF inphase bitmap using 
    * a phase accumulator
    **********************************/
    p = 0;
    for(i = 0; i < samples_for_acquire; i++) {
       if(p < samples_for_acquire/2)
         bitmap_set_bit(work_buffer, samples_for_acquire-1 - i, 1); 

       else
         bitmap_set_bit(work_buffer, samples_for_acquire-1 - i, 0); 
       p += s;       
       if(p >= samples_for_acquire) p-= samples_for_acquire;
    }

    for(i = 0; i < N_SV; i++)
    {
       struct Space_vehicle *sv;
         sv = space_vehicles+i;
       xor_to_work(sv->acquire.seek_in_phase[band], work_buffer, sv->acquire.gold_code_stretched);
#if 0
           printf("\n\n");
           print_bitmap(sv->seek_in_phase[band], samples_for_acquire);
           printf("^^^^^^^^^^^^^^^^^^^\n");
           print_bitmap(sv->gold_code_stretched, samples_for_acquire);
           printf("===================\n");
           print_bitmap(sv->seek_in_phase[band], samples_for_acquire);
#endif
    }

    /**********************************
    * Calculate IF quadrature bitmap 
    * using a phase accumulator
    **********************************/
    p = samples_for_acquire/4;
    for(i = 0; i < samples_for_acquire; i++) {
       if(p < samples_for_acquire/2)
         bitmap_set_bit(work_buffer, samples_for_acquire-1 - i, 1); 
       else
         bitmap_set_bit(work_buffer, samples_for_acquire-1 - i, 0); 
     
       p += s;
       if(p >= samples_for_acquire) p-= samples_for_acquire;
    }
    for(i = 0; i < N_SV; i++) {
       struct Space_vehicle *sv;
       sv = space_vehicles+i;
       xor_to_work(sv->acquire.seek_quadrature[band], work_buffer, sv->acquire.gold_code_stretched);
    }
  }
}

static void usage(char *message) 
{
  printf("%s\n", message);
  printf("Usage: gps -s sample_rate -i if_freq -o offset filename\n");
  exit(1);
}

/*********************************************************************
* gps_setup() - Allocate and initialise the data structures
*********************************************************************/
int gps_setup(int sample_rate, int if_freq) {
  int i, band;
  /****************************************
  * Calculate some 'almost' constants
  ****************************************/
  if(sample_rate % 1000 != 0) { 
     printf("Sample rate must be a multiple of 1000\n");
     return 0;
  }
  band_bandwidth          = 1000/ms_for_acquire;  // Hz
  search_bands            = 5000/band_bandwidth*2+1;  // For +/- 5kHz
  samples_per_ms          = sample_rate / 1000;
  code_offset_in_ms       = samples_per_ms-1;
  samples_for_acquire     = samples_per_ms * ms_for_acquire;
  acquire_min_power       = ms_for_acquire * ms_for_acquire * samples_per_ms * 2; /*  needs tuning */
  track_unlock_power      = ms_for_acquire * ms_for_acquire * samples_per_ms;     /*  needs tuning */
  lock_lost_power         = samples_per_ms*samples_per_ms/250000; /* This is over 1 ms  - needs tuning */  
  acquire_bitmap_size_u32 = (samples_for_acquire+31)/32;
  if_cycles_per_ms        = if_freq/1000;
  printf("bitmaps are %i 32-bit words in size\n",  acquire_bitmap_size_u32);
  printf("Seaching %i bands of %i Hz wide\n",search_bands, band_bandwidth);
  printf("Acquire min power %u\n",acquire_min_power);
  printf("Track lost power  %u\n",track_unlock_power);
  printf("Lock lost power   %u\n",lock_lost_power);
  /*********************************
  * Allocate memory that is used 
  * during the acquire phase
  **********************************/
  printf("Allocating memory\n");
  sample_history = malloc(acquire_bitmap_size_u32*4);
  if(sample_history == NULL) {
    printf("Out of memory for history\n");
    return 0;
  }

  work_buffer = malloc(acquire_bitmap_size_u32*4);
  if(work_buffer == NULL) {
    printf("Out of memory for history\n");
    return 0;
  }

  /*************************************************
  * Allocate per-space vehicle memory.
  *
  * As well as a stretched copy of the gold cold we
  * need space for the code mixed with the different
  * possible intermendiate frequency bitmmaps
  *************************************************/
  printf("Allocating memory for %i Space Vehicles\n", (int)N_SV);
  for(i = 0; i < N_SV; i++) {
    struct Space_vehicle *sv;
    sv = space_vehicles+i;

    sv->acquire.gold_code_stretched = malloc(acquire_bitmap_size_u32*4);
    if(sv->acquire.gold_code_stretched == NULL) {
        printf("Out of memory for gold_code_stretched\n");
        return 0;
    }

        sv->acquire.seek_in_phase       = malloc(sizeof(uint_32 *)*search_bands);
    if(sv->acquire.seek_in_phase == NULL) {
        printf("Out of memory for seek_in_phase\n");
        return 0;
    }

    sv->acquire.seek_quadrature     = malloc(sizeof(uint_32 *)*search_bands);
    if(sv->acquire.seek_quadrature == NULL) {
        printf("Out of memory for seek_quadrature\n");
        return 0;
    }

    for(band = 0; band < search_bands; band++) {        
        sv->acquire.seek_in_phase[band]            = malloc(acquire_bitmap_size_u32*4);
        if(sv->acquire.seek_in_phase[band]==NULL) {
            printf("Out of memory for sv->seek_in_phase[]\n");
            return 0;            
        }

        sv->acquire.seek_quadrature[band] = malloc(acquire_bitmap_size_u32*4);
        if(sv->acquire.seek_quadrature[band]==NULL) {
            printf("Out of memory for sv->seek_quadrature[]\n");
            return 0;            
        }
    }
  }
  
  /*************************************************
  * Now calcluate the Gold code and and populate 
  *************************************************/
  printf("Calculating Gold Codes\n");
  generateGoldCodes();
  printf("Stretching Gold Codes\n");
  stretchGoldCodes();
  printf("Mixing Gold Codes\n");
  mixLocalOscAndGoldCodes(sample_rate, if_freq);
  printf("Setup completed\n");
  return 1;
}