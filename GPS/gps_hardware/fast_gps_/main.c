#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <string.h>
#include <memory.h>
#include <math.h>
#include <time.h>
#include "setup.h"
#include "process.h"


int main(int argc, char *argv[]) 
{
	
  clock_t begin = clock();
  int upto = 1;
  int sample_rate = 16368000, if_freq = 4092000, offset = 0;
  FILE *f;
  char *filename = NULL;
  int c;

  if(argc == 1) 
  {
    usage("Must supply args");
    return 0;
  }

  while(upto < argc)
  {
     if(argv[upto][0] == '-')
     {
       if(strlen(argv[upto]) != 2) 
       {
         //usage("Only single character switches are allowed\n");
         return 0;
       }    

       if(upto == argc-1)
       {
        // usage("Missing argument for switch");
         return 0;
       }

       switch(argv[upto][1])
       {
         case 's':  sample_rate = atoi(argv[upto+1]);
                    break;
         case 'i':  if_freq     = atoi(argv[upto+1]);
                    break;
         case 'o':  offset      = atoi(argv[upto+1]);
                    break;
         default:   usage("Unknown switch");
                    return 0;
       }
       upto += 2;
     }
     else
     {
       if(filename != NULL)
       {
         usage("No file name supplied");
         return 0;
       }
       filename = argv[upto];
       upto++;
     }  
  }
  printf("Sample rate:            %i\n", sample_rate);

  printf("Intermediate Frequency: %i\n", if_freq);
  printf("Offset:                 %i\n", offset);
  printf("Filename:               %s\n", filename);
  if(sample_rate%1000 != 0)
  {
     usage("Sample rate must be divisible by 1000");
     return 0;
  } 

  f = fopen(filename, "rb");
  if(f == NULL)
  {
    printf("Unable to open file '%s'\n",filename);
  }


  /***********************************
  * Setup the internal data structures
  ***********************************/
  gps_setup(sample_rate,if_freq);
  generate_atan2_table();
  
  printf("Processing samples\n");
  c = getc(f);
  while(c != EOF) 
  {
    int i;
    for(i =0; i < 8; i++) {
      if(c&1)
        gps_process_sample(1);
      else
        gps_process_sample(0);   
      sample_count++;
      c >>= 1;
    }
    c = getc(f);
  }
  fclose(f);
  printf("%lli samples processed\n",sample_count);







  
  clock_t end=clock();
  double time_spent = (double)(end-begin)/CLOCKS_PER_SEC;
  printf("\n The program took %f seconds to run . \n ",time_spent);
  return 0;
}
