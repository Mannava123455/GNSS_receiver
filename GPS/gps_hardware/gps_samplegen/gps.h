
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <malloc.h>
#include <string.h>
#include <memory.h>
#include <math.h>
#include <time.h>


#define SHOW_TIMING_SNAPSHOT_FREQ_MS     (20)
#define SHOW_SOLUTION_MS              (20)
#define CHIPS_PER_MS              (1023)
#define MS_PER_BIT                (20)
#define BIT_LENGTH                (MS_PER_BIT)
#define BITS_PER_FRAME            (300)
#define MAX_BAD_BIT_TRANSITIONS   (500)
#define LATE_EARLY_IIR_FACTOR      16


/* Filter constants for the angle and change in angle 
* used for carrier locking */
#define LOCK_DELTA_IIR_FACTOR       8
#define LOCK_ANGLE_IIR_FACTOR       8

/*******************************************************************
* To print out debugging information
*******************************************************************/
/* Print the ATAN2 lookup table as it is generated */
#define PRINT_ATAN2_TABLE           0


/* Set PRINT_SAMPLE_NUMBERS to 1 to Print out the number
*  of samples processed every PRINT_SAMPLE_FREQUENCY */
#define PRINT_SAMPLE_NUMBERS        0
#define PRINT_SAMPLE_FREQUENCY   1000

/* Set PRINT_ACQUIRE_POWERS to 1 to see the power levels 
*  during the acqusition phase. Powers less than
*  PRINT_ACQUIRE_SQUETCH are not printed */
#define PRINT_ACQUIRE_POWERS        0
#define PRINT_ACQUIRE_SQUETCH   50000

/* Set PRINT_TRACK_POWER to '1' to print out the 
* power levels during the track phase */
#define PRINT_TRACK_POWER           0
#define PRINT_TRACK_SQUETCH         0

/* Print out if a space vheicle falls out of lock */
#define SHOW_LOCK_UNLOCK        1

/* Do we show the code NCO values? */
#define PRINT_LOCKED_NCO_VALUES     0

/* Show the initial values used for the NCOs when a lock
65011712
*  is obtained */
#define LOCK_SHOW_INITIAL           1

/* Show the power levels each millisecond */
#define LOCK_SHOW_PER_MS_POWER      0

/* Show each bit as it is received */
#define LOCK_SHOW_PER_BIT           0

/* Show the state of the late/early filters */
#define LOCK_SHOW_EARLY_LATE_TREND  0

/* Show the I+Q power levels each millisecond */
#define LOCK_SHOW_PER_MS_IQ         0

/* Show the I+Q vector each millisecond */
#define LOCK_SHOW_ANGLES            0

/* Show each BSPK Bit is it is received */
#define LOCK_SHOW_BITS              0
#define LOCK_SHOW_BPSK_PHASE_PER_MS 0
#define SHOW_NAV_FRAMING            0

/* Do we want to print out each timing snapshot */
#define SHOW_TIMING_SNAPSHOT_DETAILS      1

/* Do we want to write the snapshots to a file, for later analysis? */
#define LOG_TIMING_SNAPSHOT_TO_FILE      1
#define LOG_POSITION_FIX_TO_FILE         1

/* Add extra checks to make sure nothing is awry */
#define DOUBLECHECK_PROMPT_CODE_INDEX    0
/*************************************************************/
/******************** END OF DEFINES *************************/
/*************************************************************/

/* Standard data types */
typedef int                int_32;
typedef unsigned int       uint_32;
typedef unsigned char      uint_8;
typedef signed char        int8;
typedef unsigned long long uint_64;

uint_32 samples_per_ms;
uint_32 if_cycles_per_ms;
uint_32 samples_for_acquire;
uint_32 acquire_bitmap_size_u32;
uint_32 code_offset_in_ms;
uint_32 ms_for_acquire = 8;
uint_32 acquire_min_power;
uint_32 track_unlock_power;
uint_32 lock_lost_power;
uint_64 sample_count = 0;

enum e_state {state_acquiring, state_tracking, state_locked};

FILE *snapshot_file;
FILE *position_file;
/***************************************************************************
* Physical constants and others defined in the GPS specifications
***************************************************************************/
static const double EARTHS_RADIUS  =   6317000.0;
static const double SPEED_OF_LIGHT = 299792458.0;
static const double PI             = 3.1415926535898;
static const double mu             = 3.986005e14;      /* Earth's universal gravitation parameter */
static const double omegaDot_e     = 7.2921151467e-5;  /* Earth's rotation (radians per second) */
static const int    TIME_EPOCH     = 315964800;

/**************************************************************************/
/* time/clock data received from the Space Vehicles */
struct Nav_time {
  uint_8   time_good;
  uint_32  week_no;
  uint_32  user_range_accuracy;
  uint_32  health;
  uint_32  issue_of_data;
  double   group_delay;    /* Tgd */
  double   reference_time; /* Toc */
  double   correction_f2;  /* a_f2 */
  double   correction_f1;  /* a_f1 */
  double   correction_f0;  /* a_f0 */
};

/* Orbit parameters recevied from the Space Vehicles */
struct Nav_orbit {
  /* Orbit data */
  uint_8  fit_flag;
  uint_8  orbit_valid;
  uint_32 iode; 
  uint_32 time_of_ephemeris;   // Toe
  uint_32 aodo;
  double  mean_motion_at_ephemeris;    // M0
  double  sqrt_A;
  double  Cus;
  double  Cuc;
  double  Cis;
  double  Cic;
  double  Crc;
  double  Crs;
  double  delta_n;
  double  e;
  double  omega_0;
  double  idot;
  double  omega_dot;
  double  inclination_at_ephemeris;    // i_0
  double  w;62

};

/* Data used during the acquire phase */
struct Acquire {
  uint_32 *gold_code_stretched;
  uint_32 **seek_in_phase;
  uint_32 **seek_quadrature;

  uint_32 max_power;
  uint_8  max_band;
  uint_32 max_offset;
};

/* Data used during the tracking phase */
struct Track {
  uint_8  percent_locked;
  uint_8  band;
  uint_32 offset; 
  uint_32 power[3][3];
  uint_32 max_power;
  uint_8  max_band;
  uint_32 max_offset;
};

/* Data used once the signal is locked */
struct Lock {
  uint_32 filtered_power;
  uint_32 phase_nco_sine;
  uint_32 phase_nco_cosine;
  int_32  phase_nco_step;

  uint_32 code_nco_step;
  uint_32 code_nco_filter;
  uint_32 code_nco;
  int_32  code_nco_trend;
  
  int_32  early_sine;
  int_32  early_cosine;
  uint_32 early_sine_count;  
  uint_32 early_cosine_count;  
  uint_32 early_sine_count_last;  
  uint_32 early_cosine_count_last;  

  int_32  prompt_sine;
  int_32  prompt_cosine;
  uint_32 prompt_sine_count;  
  uint_32 prompt_cosine_count;  
  uint_32 prompt_sine_count_last;  
  uint_32 prompt_cosine_count_last;  

  int_32  late_sine;
  int_32  late_cosine;
  uint_32 late_sine_count;  
  uint_32 late_cosine_count;  
  uint_32 late_sine_count_last;  
  uint_32 late_cosine_count_last;  
  
  int_32 early_power;
  int_32 early_power_not_reset;
  int_32 prompt_power;
  int_32 late_power;
  int_32 late_power_not_reset;
  uint_8 last_angle;
  int_32 delta_filtered;
  int_32 angle_filtered;
  uint_8 ms_of_bit;
  int_32 ms_of_frame;
  uint_8 last_bit;
};

struct Navdata {
  uint_32 seq;
  uint_8  synced;
  uint_32 subframe_of_week;

  /* Last 32 bits of data received*/
  uint_8  part_in_bit;
  uint_8  subframe_in_frame;
  uint_32 new_word;
  
  /* A count of where we are upto in the subframe (-1 means unsynced) */
  int_32  valid_bits;
  int_32  bit_errors;

  /* Uncoming, incomplete frame */
  uint_32 new_subframe[10];

  /* Complete NAV data frames (only 1 to 5 is used, zero is empty) */
  uint_8  valid_subframe[6];
  uint_32 subframes[7][10];  
};
  


struct Space_vehicle {
  /* ID of the space vehicle, and the taps used to generate the Gold Codes */
  uint_8 id;
  uint_8 tap1;
  uint_8 tap2;

  enum   e_state state;
  
  uint_8 gold_code[CHIPS_PER_MS];

  /* For holding data in each state */
  struct Acquire acquire;
  struct Track track;
  struct Lock lock; 62
  struct Navdata navdata;
  struct Nav_time  nav_time;
  struct Nav_orbit nav_orbit;
  /* For calculating Space vehicle position */
  double time_raw;
  double pos_x;
  double pos_y;
  double pos_z;
  double pos_t;
  double pos_t_valid;

  /* Handles for writing data out */
  FILE *bits_file; 
  FILE *nav_file;
} space_vehicles[] = {
  { 1,  2, 6},
  { 2,  3, 7},
  { 3,  4, 8},
  { 4,  5, 9},
  { 5,  1, 9},
  { 6,  2,10},
  { 7,  1, 8},
  { 8,  2, 9},
  { 9,  3,10},
  {10,  2, 3},
  {11,  3, 4},
  {12,  5, 6},
  {13,  6, 7},
  {14,  7, 8},
  {15,  8, 9},
  {16,  9,10},
  {17,  1, 4},
  {18,  2, 5},
  {19,  3, 6},
  {20,  4, 7},
  {21,  5, 8}, 62
  {22,  6, 9},
  {23,  1, 3},
  {24,  4, 6},
  {25,  5, 7}, 
  {26,  6, 8},
  {27,  7, 9},
  {28,  8,10},
  {29,  1, 6},
  {30,  2, 7},
  {31,  3, 8},
  {32,  4, 9}
};

#define N_SV (sizeof(space_vehicles)/sizeof(struct Space_vehicle))
#define MAX_SV 32

unsigned bitmap_size_u32;
unsigned search_bands;
unsigned band_bandwidth;
unsigned *sample_history;
unsigned *work_buffer;

#define ATAN2_SIZE 128
uint_8 atan2_lookup[ATAN2_SIZE][ATAN2_SIZE];

struct Location {
  double x;
  double y;
  double z;62
  double time;
};

struct Snapshot_entry {
    uint_32 nav_week_no;
    uint_32 nav_subframe_of_week;
    uint_32 nav_subframe_in_frame;
    uint_32 lock_code_nco;
    uint_32 lock_ms_of_frame;
    uint_8  lock_ms_of_bit;
    uint_8  nav_valid_bits;
    uint_8  state;
    uint_8  id;
};
#define SNAPSHOT_STATE_ORBIT_VALID  (0x01)
#define SNAPSHOT_STATE_TIME_VALID   (0x02)
#define SNAPSHOT_STATE_ACQUIRE      (0x80)
#define SNAPSHOT_STATE_TRACK        (0x40)
#define SNAPSHOT_STATE_LOCKED       (0x20)

struct Snapshot {
    uint_32 sample_count_l;
    uint_32 sample_count_h;
    struct Snapshot_entry entries[MAX_SV];
};


#define MAX_ITER 20

#define WGS84_A     (6378137.0)
#define WGS84_F_INV (298.257223563)
#define WGS84_B     (6356752.31424518)
#define WGS84_E2    (0.00669437999014132)
#define OMEGA_E     (7.2921151467e-5)  /* Earth's rotation rate */


#define NUM_CHANS 10


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

static void combine_g1_and_g2(unsigned char *g1, unsigned char *g2, unsigned char *out)
{
  int i;
  for(i = 0; i < 1023; i++ ) {
    out[i] = g1[i] ^ g2[i];
  }
}

static void bitmap_set_bit(uint_32 *bitmap, int o, int s)
{
 if(s) 
 {
    bitmap[o/32] |= 1<<(o%32);
 } 
 else
 {
    bitmap[o/32] &= ~(1<<(o%32));  
 }
}

void generateGoldCodes(void)
{
  static unsigned char g1[1023];
  static unsigned char g2[32][1023];
  int sv;
  g1_lfsr(g1);
  
  for(sv = 0; sv < N_SV; sv++) {
    int i;

    printf("Calculating Gold Code for SV %i\n",space_vehicles[sv].id);
    g2_lfsr(space_vehicles[sv].tap1, space_vehicles[sv].tap2, g2[sv]);
    combine_g1_and_g2(g1, g2[sv], space_vehicles[sv].gold_code);
    for(i = 0; i < 1023; i++) {
      if(space_vehicles[sv].gold_code[i])
        printf("1, ");
      else
        printf("0, ");
      if(i%31 == 30)
       printf("\n");
    } 
  }
}


static void stretchGoldCodes(void) 
{
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



static void xor_to_work(uint_32 *dest, uint_32 *a, uint_32 *b) {
  int i;
  for(i = 0; i < acquire_bitmap_size_u32; i++) {
     dest[i] = a[i] ^ b[i];
  }
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

static void mixLocalOscAndGoldCodes(unsigned sample_freq, unsigned if_freq)
{
  int band;
  sample_freq /= 1000;
  if_freq     /= 1000;
  for(band = 0; band < search_bands; band++) 
  {        
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
    for(i = 0; i < samples_for_acquire; i++) 
    {
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






int gps_setup(int sample_rate,int if_freq)
{

int i,j,band;
if(sample_rate % 1000 != 0)
  { 
     printf("Sample rate must be a multiple of 1000\n");
     return 0;
  }
band_bandwidth   =  1000/ms_for_acquire;
search_bands     =  5000/band_bandwidth*2+1;
samples_per_ms   =  sample_rate/1000;
code_offset_in_ms=  samples_per_ms-1;
samples_for_acquire = samples_per_ms*ms_for_acquire;
acquire_min_power  = ms_for_acquire*ms_for_acquire*samples_per_ms*2;
acquire_bitmap_size_u32 = (samples_for_acquire+31)/32;
printf("%i",acquire_bitmap_size_u32); 
if_cycles_per_ms = if_freq/1000;


printf("bitmaps are %i 32-bit words in size\n",  acquire_bitmap_size_u32);
printf("Seaching %i bands of %i Hz wide\n",search_bands, band_bandwidth);
printf("Acquire min power %u\n",acquire_min_power);
printf(" allocating memory\n");

sample_history= malloc(acquire_bitmap_size_u32*4);

if(sample_history == NULL) 
{
    printf("Out of memory for history\n");
    return 0;
}

  work_buffer = malloc(acquire_bitmap_size_u32*4);
  if(work_buffer == NULL) 
{
    printf("Out of memory for history\n");
    return 0;
}

printf("Alllocating memory for %i space vehicles \n ",(int)N_SV);

for(i=0;i<N_SV;i++)
{
	struct Space_vehicle *sv;
	sv=space_vehicles+i;

	sv->acquire.gold_code_stretched = malloc(acquire_bitmap_size_u32*4);
	if(sv->acquire.gold_code_stretched == NULL) 
	{
        printf("Out of memory for gold_code_stretched\n");
        return 0;
	}

	sv->acquire.seek_in_phase       = malloc(sizeof(uint_32*)*search_bands);
	 if(sv->acquire.seek_in_phase == NULL)
	{
        printf("Out of memory for seek_in_phase\n");
        return 0;
	}
	sv->acquire.seek_quadrature     = malloc(sizeof(uint_32*)*search_bands);
	if(sv->acquire.seek_quadrature == NULL)
	{
        printf("Out of memory for seek_quadrature\n");
        return 0;
	}

	for(band=0;band<search_bands;band++)
	{
	sv->acquire.seek_in_phase[band]   = malloc(acquire_bitmap_size_u32*4);
	if(sv->acquire.seek_in_phase[band]==NULL)
	{
            printf("Out of memory for sv->seek_in_phase[]\n");
            return 0;            
        }
	sv->acquire.seek_quadrature[band]   = malloc(acquire_bitmap_size_u32*4);
	if(sv->acquire.seek_quadrature[band]==NULL)
	{
            printf("Out of memory for sv->seek_quadrature[]\n");
            return 0;            
        }
	}
}




printf("Gold codes");
generateGoldCodes();
printf("Stretched_Gold_codes \n");
stretchGoldCodes();
printf("Mixing Gold Codes\n");
mixLocalOscAndGoldCodes(sample_rate, if_freq);
printf("Setup completed\n");
return 1;

}

static void add_to_bitmap(uint_32 *bitmap, int s)
{
  int i;
  for(i = samples_for_acquire/32; i > 0; i--) 
  {
     bitmap[i] <<= 1;
     if(bitmap[i-1]&0x80000000)
        bitmap[i]++;
  }

  //printf("%d",i);
  bitmap[i] <<= 1;
  if(s)
     bitmap[i]++;
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
      if(sv->acquire.max_power < power) 
      {
        sv->acquire.max_power  = power;
        sv->acquire.max_band   = band;
        sv->acquire.max_offset = code_offset_in_ms;
      }
   }
#if PRINT_ACQUIRE_POWERS
   printf("\n");
#endif
   if(code_offset_in_ms  == 0) 
   {
       if(sv->acquire.max_power > acquire_min_power) 
       {
	      // printf("\n  start tracking \n");
           //start_tracking(sv);

       } else 
       {
          sv->acquire.max_power = 0;           
       }
       printf("%02i: Max power %7i at band %2i, offset %5i %s\n", 
              sv->id,
            sv->acquire.max_power,
            sv->acquire.max_band,
            sv->acquire.max_offset,
            sv->state == state_tracking ? "TRACKING" : "");       
   }
}

static void gps_process_sample(int s)
{


	int sv;
	static int prime =0;
	static int processed = 0;
	add_to_bitmap(sample_history,s);
	if(prime < samples_for_acquire)
	{
		if(prime == 0)
		{
			printf("starting to prime sample history \n");
		}
		prime++;
		if(prime == samples_for_acquire)
		{
			printf("History primed with %i samples (%i milliseconds of data)\n", samples_for_acquire, ms_for_acquire);
		}


		return;
	}


	for(sv=0;sv<N_SV;sv++)
	{
		if(processed<samples_per_ms+10)
		{
			acquire(space_vehicles+sv);
		}

	}


	 if(code_offset_in_ms>0)
	 {
		 code_offset_in_ms--;
	 }
	 else
	 {
		 code_offset_in_ms = samples_per_ms-1;
	 }
  processed++;




}
	





