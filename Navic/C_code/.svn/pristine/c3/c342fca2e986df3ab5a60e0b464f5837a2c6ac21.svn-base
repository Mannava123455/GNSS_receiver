#include<stdio.h>
#include<stdlib.h>
#include<malloc.h>
#include<complex.h>



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
double complex *fun1(double **x, int sc) {
    double complex *in;
    in = (double complex*) malloc(sc * sizeof(double complex));
    int i;
    for(i = 0; i < sc; i++) {
        in[i] = x[i][0];
    }
    return in;
}



int main()
{
double **received;
received=createMat(10230,2);
double complex *r;
int sc = 5;
r = fun1(received, sc);
for(int j = 0; j < sc; j++) {
    printf("%lf %lf\n", creal(r[j]), cimag(r[j]));
}
return 0;
}
