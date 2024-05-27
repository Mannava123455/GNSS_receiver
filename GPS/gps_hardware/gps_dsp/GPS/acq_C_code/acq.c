#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include "samples1.h"




int SVs[] = {
  2,
  6,
  3,
  7,
  4,
  8,
  5,
  9,
  1,
  9,
  2,
  10,
  1,
  8,
  2,
  9,
  3,
  10,
  2,
  3,
  3,
  4,
  5,
  6,
  6,
  7,
  7,
  8,
  8,
  9,
  9,
  10,
  1,
  4,
  2,
  5,
  3,
  6,
  4,
  7,
  5,
  8,
  6,
  9,
  1,
  3,
  4,
  6,
  5,
  7,
  6,
  8,
  7,
  9,
  8,
  10,
  1,
  6,
  2,
  7,
  3,
  8,
  4,
  9
};

unsigned char gold_code[1023];

static void g1_lfsr(unsigned char * out) 
{
  int state = 0x3FF, i, new_bit;
  for (i = 0; i < 1023; i++)
   {
    out[i] = (state >> 9) & 0x1;
    new_bit = ((state >> 9) ^ (state >> 2)) & 1;
    state = ((state << 1) | new_bit) & 0x3FF;
  }
}

static void g2_lfsr(unsigned char tap0, unsigned char tap1, unsigned char * out)
{
  int state = 0x3FF, i;
  /* Adjust tap number from 1-10 to 0-9 */
  tap0--;
  tap1--;
  for (i = 0; i < 1023; i++) {
    int new_bit;
    out[i] = (((state >> tap0) ^ (state >> tap1)) & 0x1);
    /* Update the G2 LFSR  */
    new_bit = ((state >> 9) ^ (state >> 8) ^
      (state >> 7) ^ (state >> 5) ^
      (state >> 2) ^ (state >> 1)) & 1;
    state = ((state << 1) | new_bit) & 0x3FF;
  }
}

static void combine_g1_and_g2(unsigned char * g1, unsigned char * g2, unsigned char * out) 
{
  int i;
  for (i = 0; i < 1023; i++) 
  {
    out[i] = g1[i] ^ g2[i];
  }
}

static void bitmap_set_bit(unsigned int * bitmap, int o, int s) 
{
  if (s) 
  {
    bitmap[o / 32] |= 1 << (o % 32);
  } 
  else 
  {
    bitmap[o / 32] &= ~(1 << (o % 32));
  }
}

static void add_to_bitmap(unsigned int * bitmap, int s) 
{
  int i;
  for (i = 128; i > 0; i--) 
  {
    bitmap[i] <<= 1;
    if (bitmap[i - 1] & 0x80000000)
      bitmap[i]++;
  }

  //printf("%d",i);
  bitmap[i] <<= 1;
  if (s)
    bitmap[i]++;
}

static void xor_to_work(unsigned int * dest, unsigned int * a, unsigned int * b) 
{
  int i;
  for (i = 0; i < 128; i++) 
  {
    dest[i] = a[i] ^ b[i];
  }
}

static int count_one_bits(unsigned int * a, int i) 
{
  int count = 0;
  int j;
  unsigned char * b = (unsigned char * ) a;

  static int one_bits[256];
  static int setup = 1;

  if (setup) 
  {
    for (j = 0; j < 256; j++) 
    {
      one_bits[j] = 0;
      if (j & 0x01) one_bits[j]++;
      if (j & 0x02) one_bits[j]++;
      if (j & 0x04) one_bits[j]++;
      if (j & 0x08) one_bits[j]++;
      if (j & 0x10) one_bits[j]++;
      if (j & 0x20) one_bits[j]++;
      if (j & 0x40) one_bits[j]++;
      if (j & 0x80) one_bits[j]++;
    }
    setup = 0;
  }

  count = 0;
  while (i >= 8) 
  {
    count += one_bits[b[0] & 0xFF];
    i -= 8;
    b++;
  }

  for (j = 0; j < i; j++) 
  {
    if (b[0] & (1 << j))
      count++;
  }
  return count;
}

int main() 
{




  /**** Declarations ******/

  int sample_freq = 2048000;
  int if_freq = 1000000;
  int k = 0, i, j, m, n, band, s, p, z;
  int sin_power;
  int cos_power;
  int power;
  int max_band;
  int max_code_offset;
  int ms_for_acquire = 2;
  int band_bandwidth = 1000 / ms_for_acquire;
  int search_bands = 5000 / band_bandwidth * 2 + 1;
  int samples_per_ms = 2048000 / 1000;
  int samples_for_acquire = samples_per_ms * ms_for_acquire;
  int acquire_min_power = ms_for_acquire * ms_for_acquire * samples_per_ms * 2;
  int acquire_bitmap_size_u32 = (samples_for_acquire) / 32;

  /**** Array initialisations   *******/

  static unsigned char g1[1023];
  static unsigned char g2[1023];
  unsigned char gold_code[1023];
  unsigned int * gold_code_stretched;
  unsigned int * sample_history;
  unsigned int * work_buffer;
  unsigned int * in_phase;
  unsigned int * quadrature_phase;

  gold_code_stretched = (unsigned int * ) malloc(acquire_bitmap_size_u32 * 4);
  sample_history = (unsigned int * ) malloc(acquire_bitmap_size_u32 * 4);
  work_buffer = (unsigned int * ) malloc(acquire_bitmap_size_u32 * 4);
  in_phase = (unsigned int * ) malloc(acquire_bitmap_size_u32 * 4);
  quadrature_phase = (unsigned int * ) malloc(acquire_bitmap_size_u32 * 4);






  int sv;
  g1_lfsr(g1);
 
  sample_freq /= 1000;
  if_freq /= 1000;

  /*** Loop for all 32 satellites ****/

  for (sv = 0; sv < 32; sv++) 
  
  {

    /*** loop for code offset ****/

    printf("satellite = %d\n", sv + 1);
    for (j = 0; j < 512; j++) 
    {
      for (i = 7; i >= 0; i--) 
      {
        if ((samples[j] >> i) & 1) 
        {
          add_to_bitmap(sample_history, 1);
        } 
        else
        {
          add_to_bitmap(sample_history, 0);

        }
      }
    }

    int code_offset_in_ms = samples_per_ms - 1;
    //printf("\n Calculating Gold Code for SV %d \n",sv+1);
    int i;

    /** prn code generation ***/

    unsigned char tap1 = SVs[k++];
    unsigned char tap2 = SVs[k++];

    g2_lfsr(tap1, tap2, g2);
    combine_g1_and_g2(g1, g2, gold_code);


    /*** upsampling ****/
    for (j = 0; j < samples_for_acquire; j++) 
    {

      int index = (j * 1023 / samples_per_ms) % 1023;
      bitmap_set_bit(gold_code_stretched,
        samples_for_acquire - 1 - j,
        gold_code[index]);
    }

    int max = 0;



    for (m = 512; m < 768; m++)
     {
      for (n = 7; n >= 0; n--)
       {
        if ((samples[m] >> n) & 1) 
        {
          add_to_bitmap(sample_history, 1);
        } 
        else
        {
          add_to_bitmap(sample_history, 0);
        }

        for (band = 0; band < 21; band++) 
        {
          s = samples_for_acquire * if_freq / sample_freq + band - search_bands / 2;


          p = 0;
          for (i = 0; i < samples_for_acquire; i++) 
          {
            if (p < samples_for_acquire / 2)
              bitmap_set_bit(work_buffer, samples_for_acquire - 1 - i, 1);
            else
              bitmap_set_bit(work_buffer, samples_for_acquire - 1 - i, 0);
            p += s;
            if (p >= samples_for_acquire)
              p -= samples_for_acquire;
          }
          xor_to_work(in_phase, work_buffer, gold_code_stretched);



          p = samples_for_acquire / 4;
          for (i = 0; i < samples_for_acquire; i++) 
          {
            if (p < samples_for_acquire / 2)
              bitmap_set_bit(work_buffer, samples_for_acquire - 1 - i, 1);
            else
              bitmap_set_bit(work_buffer, samples_for_acquire - 1 - i, 0);
            p += s;
            if (p >= samples_for_acquire)
              p -= samples_for_acquire;
          }


          xor_to_work(quadrature_phase, work_buffer, gold_code_stretched);
          xor_to_work(work_buffer, sample_history, in_phase);
          sin_power = count_one_bits(work_buffer, samples_for_acquire) - samples_for_acquire / 2;

          xor_to_work(work_buffer, sample_history, quadrature_phase);
          cos_power = count_one_bits(work_buffer, samples_for_acquire) - samples_for_acquire / 2;

          power = sin_power * sin_power + cos_power * cos_power;

          if (power > max) 
          {
            max = power;
            max_band = band;
            max_code_offset = code_offset_in_ms;
          }

        }
        code_offset_in_ms--;

      }

    }

    printf("Power = %d\n", max);
    printf("Doppler frequency = %d\n", -5000 + 500 * max_band);
    printf("code phase = %d\n", max_code_offset);
    printf(" \n ");



  }

}
