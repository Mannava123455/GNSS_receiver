#include<stdio.h>
#include<stdlib.h>
#include<malloc.h>
#include<math.h>
#include<complex.h>
#include<fftw3.h>
#include<malloc.h>
#define PI 3.141592653589793



double **createMat(int m,int n);
double *loadtxta(char *str,int m);
int **createMatint(int m,int n);
int **transposeint(int **a,  int m, int n);
int len(double *arr); 
double complex **createMat_complex(int m,int n);
int *genNavicCaCode(int s);
int **genNavicCatable(double samplingFreq);
int *arange(int m,int n,int step);
void pmfint(char *str, int **a,int r,int c); 
void pmf(char *str, double **a,int r,int c);
void pmfarr(char *str,double *a,int sc); 


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

double complex  **createMat_complex(int m,int n)
{
 int i;
 double complex **a;
 
 //Allocate memory to the pointer
a = (double complex **)malloc(m * sizeof( *a));
    for (i=0; i<m; i++)
         a[i] = (double complex *)malloc(n * sizeof( *a[i]));

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

double **transpose(double **a,  int m, int n)
{
int i, j;
double **c;
//printf("I am here");
c = createMat(n,m);

 for(i=0;i<n;i++)
 {
  for(j=0;j<m;j++)
  {
c[i][j]= a[j][i];
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


int len(double *arr) 
{
    int length = 0;
    while (*arr) 
    { 
        length++;
        arr++;
    }
    return length;
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


