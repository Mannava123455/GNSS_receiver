#include <stdio.h>
#include <stdlib.h>

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


int main()
{
    const char *file_name = "gpssim.bin";
    FILE *file;
    file = fopen(file_name, "rb");
    if (file == NULL)
    {
        perror("Error opening file");
        return 1;
    }

    int c;
    while ((c = fgetc(file)) != EOF) 
    {
        for (int i=0;i<8;i++) 
	{
            if (c&1) 
	    {
                printf("1");
            }
	    else 
	    {
                printf("0");
            }
	    c>>=1;
        }
    }


    return 0;
}

