#include<math.h>
#include<stdio.h>
#include<stdlib.h>
#include<malloc.h>


double *createarr(int m);
void print(double **p, int m,int n);
void printarr(double *p,int n);
double **loadtxt(char *str,int m,int n);
void readMat(double **p, int m,int n);
void readarr(double *p, int n);
int *createarrint(int m);
void printmatint(int **p, int m,int n);
void printarrint(int *p, int n);







int *createarrint(int m)
{
 int i;
 int *a;
 
a = (int *)malloc(m * sizeof(int));
 return a;
}



void printarrint(int *p, int n)
{
 int i;

 for(i=0;i<n;i++)
 {
  printf("%d ",p[i]);
}
}

void readarr(double *p, int n)
{
 int i;
 for(i=0;i<n;i++)
 {
   scanf("%lf",&p[i]);
 }
}
void readMat(double **p, int m,int n)
{
 int i,j;
 for(i=0;i<m;i++)
 {
  for(j=0;j<n;j++)
  {
   scanf("%lf",&p[i][j]);
  }
 }
}

void printarr(double *p, int n)
{
 int i;

 for(i=0;i<n;i++)
 {
  printf("%lf \n",p[i]);
}
}

void print(double **p, int m,int n)
{
 int i,j;

 for(i=0;i<m;i++)
 {
  for(j=0;j<n;j++)
  {
  printf("%lf ",p[i][j]);
  }
 printf("\n");
 }
}

void printmatint(int **p, int m,int n)
{
 int i,j;

 for(i=0;i<m;i++)
 {
  for(j=0;j<n;j++)
  {
  printf("%d ",p[i][j]);
  }
 printf("\n");
 }
}

double *createarr(int m)
{
 int i;
 double *a;
 
a = (double *)malloc(m * sizeof(double));
 return a;
}





double **loadtxt(char *str,int m,int n)
{
FILE *fp;
double **a;
int i,j;


a = createMat(m,n);
fp = fopen(str, "r");

 for(i=0;i<m;i++)
 {
  for(j=0;j<n;j++)
  {
   fscanf(fp,"%lf",&a[i][j]);
  }
 }
}



