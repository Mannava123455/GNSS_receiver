#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <string.h>
#include <memory.h>
#include <math.h>
#include <time.h>
#include"acq.h"



int main()
{
	//int sample_rate=5456000;
	int if_freq= 1015000;
	//int if_freq= 1000000;
	int sample_rate=2048000;
//	int if_freq= 0;
	gps_setup(sample_rate,if_freq);
//	const char *file_name = "gps.bin";
	const char *file_name = "iq_if.bin";
	FILE *fiq;
	fiq=fopen(file_name,"r");
	if(fiq==NULL)
	{
		perror("Error inka poyyi paduko");
		return 1;
	}

	int c;
	while((c=fgetc(fiq)) !=EOF)
	{
		for(int i=0;i<8;i++)
		{
			if(c&1)
			{
				gps_process_sample(1);
			}
			else
			{
				gps_process_sample(0);

			}
			  //sample_count++;
			c>>=1;
		}
	}


/*c = getc(fiq);
while (c != EOF)
{
    int i;
    for (i = 7; i >= 0; i--)
    { 
        if ((c >> i) & 1)
	{
            gps_process_sample(1);
	}
        else
	{
            gps_process_sample(0);
	}
        sample_count++;
    }
    c = getc(fiq);
}*/

	  fclose(fiq);
 	 // printf("%lli samples processed\n",sample_count);
	return 0;
}


