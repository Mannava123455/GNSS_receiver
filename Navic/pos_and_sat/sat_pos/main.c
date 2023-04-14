#include<stdio.h>
#include<stdlib.h>
#include<malloc.h>
#include"lib.h"
int main()
{

int *x,s,i;
x=(int *)malloc(1024*sizeof(int));
printf("Enter the satellite id :");
scanf("%d",&s);
x=genNavicCaCode(s);
for(i=0;i<1023;i++)
{
	printf("%d",x[i]);
}
return 0;
}
