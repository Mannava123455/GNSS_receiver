#include<stdio.h>
#include<stdlib.h>
#include<math.h>
#include<fftw3.h>
#include<complex.h>
int main()
{

typedef double complex cplx;

cplx a[10];
int i;
for(i=0;i<10;i++)
{
	a[i]=1+I;
}

for(i=0;i<10;i++)
{
	printf("%lf,%lf\n",creal(a[i]),cimag(a[i]));

}
return 0;
}

