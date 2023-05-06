#include <stdio.h>
#include <stdlib.h>
#include <fftw3.h>
#include <complex.h>
#include"lib.h"

double complex **fft2d1(double complex **in, int nrow, int ncol) 
{
    fftw_complex *in_row = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * ncol);
    fftw_complex *out_row = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * ncol);

    fftw_plan plan_forward = fftw_plan_dft_1d(ncol, in_row, out_row, FFTW_FORWARD, FFTW_ESTIMATE);
    fftw_plan plan_backward = fftw_plan_dft_1d(ncol, in_row, out_row, FFTW_BACKWARD, FFTW_ESTIMATE);
    double complex **out;
    out=createMat_complex(nrow,ncol);
    for(int i = 0; i < nrow; i++) 
    {
        for(int j = 0; j < ncol; j++) 
	{
            in_row[j][0] = creal(in[i][j]);
            in_row[j][1] = cimag(in[i][j]);
        }

        fftw_execute(plan_backward);

        for(int j = 0; j < ncol; j++) 
	{
            out[i][j] = (out_row[j][0] + out_row[j][1] * I)/ncol;
        }
    }

    // Free memory and destroy plans
    fftw_destroy_plan(plan_forward);
    fftw_destroy_plan(plan_backward);
    fftw_free(in_row);
    fftw_free(out_row);
    return out; 
}

int main()
{
    // Create a sample 2D matrix
    int nrow = 3, ncol = 3;
    double complex **in = (double complex**) malloc(sizeof(double complex*) * nrow);
    double complex **out = (double complex**) malloc(sizeof(double complex*) * nrow);
    for(int i = 0; i < nrow; i++) 
    {
        in[i] = (double complex*) malloc(sizeof(double complex) * ncol);
        out[i] = (double complex*) malloc(sizeof(double complex) * ncol);
        for(int j = 0; j < ncol; j++)
	{
            in[i][j] = 1+I;
        }
    }


    out=fft2d1(in, nrow, ncol);

    printf("Input matrix:\n");
    for(int i = 0; i < nrow; i++) {
        for(int j = 0; j < ncol; j++) {
            printf("%.2lf + %.2lfi\t", creal(in[i][j]), cimag(in[i][j]));
        }
        printf("\n");
    }
    printf("\n");

    printf("Output matrix:\n");
    for(int i = 0; i < nrow; i++) 
    {
        for(int j = 0; j < ncol; j++) 
	{
            printf("%.2lf + %.2lfi\t", creal(out[i][j]), cimag(out[i][j]));
        }
        printf("\n");
    }
}


