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
	int sample_rate=5456000;
	int if_freq= 4092000;
	gps_setup(sample_rate,if_freq);


	return 0;
}


