
#include<stdio.h>
#include<stdlib.h>
#include<malloc.h>
#include<math.h>
int **createMatint(int m,int n);
int *genNavicCaCode(int s);
int **genNavicCatable(double samplingFreq);
int *arange(int n);


int **createMatint(int m,int n)
{
 int i;
 int **a;
 
 //Allocate memory to the pointer
a = (int **)malloc(m * sizeof( *a));
    for (i=0; i<m; i++)
         a[i] = (int *)malloc(n * sizeof( *a[i]));

 return a;
}
int *arange(int n)
{
	int *a;
	a=(int*)malloc(n*sizeof(int));
	int i;
	for(i=0;i<n;i++)
	{
		a[i]=i;
	}
	return a;
}


int *genNavicCaCode(int s)
{

int i,j;
int L5[28][10]={{1,1,1,0,1,0,0,1,1,1},
	    {0,0,0,0,1,0,0,1,1,0},
	    {1,0,0,0,1,1,0,1,0,0},
	    {0,1,0,1,1,1,0,0,1,0},
	    {1,1,1,0,1,1,0,0,0,0},
	    {0,0,0,1,1,0,1,0,1,1},
	    {0,0,0,0,0,1,0,1,0,0},
	    {0,1,0,0,1,1,0,0,0,0},
	    {0,0,1,0,0,1,1,0,0,0},
	    {1,1,0,1,1,0,0,1,0,0},
	    {0,0,0,1,0,0,1,1,0,0},
	    {1,1,0,1,1,1,1,1,0,0},
	    {1,0,1,1,0,1,0,0,1,0},
	    {0,1,1,1,1,0,1,0,1,0},
	    {0,0,1,1,1,0,1,1,1,1},
	    {0,1,0,1,1,1,1,1,0,1},
	    {1,0,0,0,1,1,0,0,0,1},
	    {0,0,1,0,1,0,1,0,1,1},
	    {1,0,1,0,0,1,0,0,0,1},
	    {0,1,0,0,1,0,1,1,0,0},
	    {0,0,1,0,0,0,1,1,1,0},
	    {0,1,0,0,1,0,0,1,1,0},
	    {1,1,0,0,0,0,1,1,1,0},
	    {1,0,1,0,1,1,1,1,1,0},
	    {1,1,1,0,0,1,0,0,0,1},
	    {1,1,0,1,1,0,1,0,0,1},
	    {0,1,0,1,0,0,0,1,0,1},
	    {0,1,0,0,0,0,1,1,0,1}};

int G1[10],G2[10],c1[1024],c2[1024];
int *CA;
int *a;
CA=(int *)malloc(1024*sizeof(int));
a=(int*)malloc(1*sizeof(int));
a[0]=1;

for(i=0;i<10;i++)
{
	G1[i] = 1;
}
if (s<0 || s>28)
{
	return a;
}
else if (s<28)
{
for(i=0;i<10;i++)
{
G2[i] = L5[s][i];
}
}

int k, temp;
for(k=0;k<1024;k++)
{
c1[k]=G1[9];
temp = G1[2]^G1[9];;
for (i = 9; i > 0; i--) 
{
G1[i] = G1[i - 1];    
}
G1[0] = temp;
}


for(k=0;k<1024;k++)
{
c2[k]=G2[9];
temp = G2[1]^G2[2]^G2[5]^G2[7]^G2[8]^G2[9];
for (i = 9; i > 0; i--) 
{
G2[i] = G2[i - 1];    
}

G2[0] = temp;
}


for(j=0;j<1023;j++)
{
CA[j]=c1[j]^c2[j];
}

return CA;
}

int **genNavicCatable(double samplingFreq)
{
	int prnIdMax=14;
	int i,j;
	int codeLength=1023;
	double codeFreq=1.023*pow(10,6);
	double samplingPeriod=1/samplingFreq;
	double sampleCount = (int)(samplingFreq/(codeFreq/codeLength));
	int sc;
	sc=(int)sampleCount;
	int *r;
	r=(int *)malloc(sc*sizeof(int));
	r=arange(sc);
	for(i=0;i<sc;i++)
	{
		r[i]=r[i]*codeFreq*samplingPeriod;
	}
	int **table;
	table=createMatint(prnIdMax,codeLength);
	for(i=0;i<prnIdMax;i++)
	{
		int *dummy=genNavicCaCode(i);
		for(j=0;j<codeLength;j++)
		{
			table[i][j]=dummy[j];
		}
		free(dummy);
	}

	int ** codeTable;
	codeTable=createMatint(14,10230);
	for(i=0;i<14;i++)
	{
		for(j=0;j<10230;j++)
		{
			codeTable[i][j]=table[i][r[j]];
		}
	}



	return codeTable;	
}

	

	




