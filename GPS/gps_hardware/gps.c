#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>
#include <string.h>
#include <memory.h>
#include <math.h>
#include <time.h>
#include"gps.h"



int main()
{
	int sample_rate=2000000;
	int if_freq= 0;
	gps_setup(sample_rate,if_freq);
	const char *file_name = "gpssim.bin";
	FILE *fiq;
	fiq=fopen(file_name,"rb");
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
			c>>=1;
		}
	}

	return 0;
}


