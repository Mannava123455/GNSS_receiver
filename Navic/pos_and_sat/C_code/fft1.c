#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <fftw3.h>

#define N 16

int main() 
{
    double *in;
    fftw_complex *out;
    fftw_plan plan;
    
    in = (double*) fftw_malloc(sizeof(double) * N);
    out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * N);
    
    for (int i = 0; i < N; i++) {
        in[i] = 1 + I*1; // Initialize the input array with real and imaginary values
    }

    plan = fftw_plan_dft_r2c_1d(N, in, out, FFTW_ESTIMATE);
    fftw_execute(plan);

    printf("FFT of the input sequence:\n");
    for (int i = 0; i < N/2+1; i++) {
        printf("%d: %g + %gi\n", i, creal(out[i]), cimag(out[i]));
    }

    fftw_destroy_plan(plan);
    fftw_free(in);
    fftw_free(out);

    return 0;
}

