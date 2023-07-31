#include<stdio.h>
#include<stdlib.h>
#include<malloc.h>
#include<math.h>
#include<complex.h>
#include<fftw3.h>




double **createMat(int m,int n);
double *loadtxta(char *str,int m);
int **createMatint(int m,int n);
int **transposeint(int **a,  int m, int n);
int *genNavicCaCode(int s);
int **genNavicCatable(double samplingFreq);
int *arange(int m,int n,int step);
double **receivedsignal(double *a,double *b,int sc);
double **fft_complex(double **a,int sc);
double **fft_real(double *a,int sc);
void pmfint(char *str, int **a,int r,int c); 
void pmf(char *str, double **a,int r,int c);
void pmfarr(char *str,double *a,int sc); 
//double **acquisition(double **x,double **prn,int ip,double fs,double *fsearch,int threshold,int sc);


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



double **createMat(int m,int n)
{
 int i;
 double **a;
 
 //Allocate memory to the pointer
a = (double **)malloc(m * sizeof( *a));
    for (i=0; i<m; i++)
         a[i] = (double *)malloc(n * sizeof( *a[i]));

 return a;
}



int **transposeint(int **a,  int m, int n)
{
int i, j;
int **c;
//printf("I am here");
c = createMatint(n,m);

 for(i=0;i<n;i++)
 {
  for(j=0;j<m;j++)
  {
c[i][j]= a[j][i];
//  printf("%lf ",c[i][j]);
  }
 }
return c;

}

int *arange(int m,int n,int step)
{
	int *a;
	a=(int*)malloc(n*sizeof(int));
	int i;
	for(i=m;i<n;i=i+step)
	{
		a[i]=i;
	}
	return a;
}





double *loadtxta(char *str,int m)
{

FILE *fp;
double *a;
int i;
a=(double*)malloc(m*sizeof(double));
fp = fopen(str, "r");
for(i=0;i<m;i++)
{
fscanf(fp,"%lf",&a[i]);
}
fclose(fp);
return a;

}

void pmf(char *str, double **a,int r,int c)  
{
int i,j;
FILE *fp;
fp = fopen(str,"w");
for (i = 0; i < r; i++)
{
for(j=0;j<c;j++)
{
fprintf(fp,"%lf ",a[i][j]);
}
fprintf(fp,"\n");
}
}
void pmfint(char *str, int **a,int r,int c)  
{
int i,j;
FILE *fp;
fp = fopen(str,"w");
for (i = 0; i < r; i++)
{
for(j=0;j<c;j++)
{
fprintf(fp,"%d ",a[i][j]);
}
fprintf(fp,"\n");
}
}


void pmfarr(char *str,double *a,int sc)  
{
FILE *fp;
fp = fopen(str,"w");
int i;
for(i=0;i<sc;i++)
{
fprintf(fp,"%lf\n",a[i]);
}
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
	r=arange(0,sc,1);
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

	int ** codeTable1;
	codeTable1=createMatint(14,10230);
	for(i=0;i<14;i++)
	{
		for(j=0;j<10230;j++)
		{
			codeTable1[i][j]=table[i][r[j]];
		}
	}
	int **codeTable;
	codeTable=createMatint(10230,14);
	codeTable=transposeint(codeTable1,14,10230);
	return codeTable;	
}



double **receivedsignal(double *a,double *b,int sc)
{
	int i,j;
	double **c;
	c=createMat(sc,2);
	for(i=0;i<sc;i++)
	{
		c[i][0]=a[i];
	}
	for(i=0;i<sc;i++)
	{
		c[i][1]=b[i];
	}

	return c;
}

double **fft_complex(double **a,int sc)
{
	fftw_complex  *in;
	fftw_complex *out;
	fftw_plan plan;
        in = (fftw_complex *) fftw_malloc(sizeof(fftw_complex) * sc);
        out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * sc);
	
    for (int i = 0; i < sc; i++) 
    {
        in[i] = a[i][0] + I*a[i][1];
    }

    plan = fftw_plan_dft_1d(sc, in, out,FFTW_FORWARD,FFTW_ESTIMATE);
    fftw_execute(plan);
    double **b;
    b=createMat(sc,2);
    for (int i = 0; i < sc; i++) 
    {
	    b[i][0]=creal(out[i]);
        
    }
    for (int i = 0; i < sc; i++) 
    {
	    b[i][1]=cimag(out[i]);
        
    }
    return b;
}


double **fft_real(double *a,int sc)
{
	fftw_complex  *in;
	fftw_complex *out;
	fftw_plan plan;
        in = (fftw_complex *) fftw_malloc(sizeof(fftw_complex) * sc);
        out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * sc);
	
    for (int i = 0; i < sc; i++) 
    {
        in[i] = a[i];
    }

    plan = fftw_plan_dft_1d(sc, in, out,FFTW_FORWARD,FFTW_ESTIMATE);
    fftw_execute(plan);
    double **b;
    b=createMat(sc,2);
    for (int i = 0; i < sc; i++) 
    {
	    b[i][0]=creal(out[i]);
        
    }
    for (int i = 0; i < sc; i++) 
    {
	    b[i][1]=cimag(out[i]);
        
    }
    return b;
}



