#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <fftw3.h>

int main()
{
    // Define some variables
    int n = 8;
    int i;

    // Allocate memory for input and output arrays
    double* in = (double*) fftw_malloc(sizeof(double) * n);
    fftw_complex* out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * n);

    // Define a plan for the FFT
    fftw_plan p = fftw_plan_dft_r2c_1d(n, in, out, FFTW_ESTIMATE);

    // Define some test data
    for (i = 0; i < n; i++) {
        in[i] = sin(2*M_PI*i/n) + cos(4*M_PI*i/n);
    }

    // Compute the FFT
    fftw_execute(p);

    // Print the original and transformed data
    printf("Original data:\n");
    for (i = 0; i < n; i++) {
        printf("%f\n", in[i]);
    }

    printf("Transformed data:\n");
    for (i = 0; i < n; i++) {
        printf("%f + %fi\n", out[i][0], out[i][1]);
    }

    // Free memory and destroy the plan
    fftw_destroy_plan(p);
    fftw_free(in);
    fftw_free(out);

    return 0;
}

