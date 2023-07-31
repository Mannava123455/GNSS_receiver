#include <stdio.h>
#include <stdlib.h>

int main() 
{
    // open the file for reading
    FILE* fp = fopen("real.txt", "r");

    if (fp == NULL) 
    {
        printf("Error opening file\n");
        exit(1);
    }

    // allocate memory for the array
    const int MAX_NUMS = 100; // maximum number of elements in the array
     long double nums[MAX_NUMS];
     long double value;;

    int i;
    for(i=0;i<MAX_NUMS;i++)
    {
	    fscanf(fp,"%Lf",&value);
	    nums[i]=value;
    }

    // close the file
    fclose(fp);

    // print the array to verify the values are correct
    long double a;
    a=nums[1];
    for (int i = 0; i < 100; i++) 
    {
        printf("%Lf\n", nums[i]);
    }

    return 0;
}

