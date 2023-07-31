#include<stdio.h>
#include<math.h>
#include<stdlib.h>
#include<malloc.h>
#include<fftw3.h>
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

complex  *fftd_complex(double **a,int sc)
{
	int i;
	fftw_complex  *in;
	fftw_complex *out;
	fftw_plan plan;
        in = (fftw_complex *) fftw_malloc(sizeof(fftw_complex) * sc);
        out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * sc);
	
    for (i = 0; i < sc; i++) 
    {
        in[i]=a[i][0] + I*a[i][1];
    }

    plan = fftw_plan_dft_1d(sc, in, out,FFTW_FORWARD,FFTW_ESTIMATE);
    fftw_execute(plan);
complex double *x;
    x = (complex double *) fftw_malloc(sizeof(complex double) * sc);
    for(i=0;i<sc;i++)
    {
	    x[i]=out[i];
    }


    return x;
}


int main()
{
	int sc=10;
	complex double *x;
        x = (complex double*) fftw_malloc(sizeof(complex double) * sc);
	double **y;
	y=createMat(sc,2);
	int i,j;
	for(i=0;i<sc;i++)
	{
		for(j=0;j<2;j++)
		{
			y[i]=1;
		}
	}

	x=fftd_complex(y,sc);

	for(i=0;i<sc;i++)
	{
		printf("%lf %lf",creal(x[i]),cimag(x[i]));
	}



}
