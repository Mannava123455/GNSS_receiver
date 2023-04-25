#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <fftw3.h>

#define N 16

int main() {
    int i;
    fftw_complex in[N], out[N];
    fftw_plan plan;

    // Generate input data
    for (i = 0; i < N; i++) {
        in[i][0] = 0;
        in[i][1] = 1;
    }

    // Create plan and execute FFT
    plan = fftw_plan_dft_1d(N, in, out, FFTW_FORWARD, FFTW_ESTIMATE);
    fftw_execute(plan);
    fftw_destroy_plan(plan);

    // Print output
    for (i = 0; i < N; i++) {
        printf("%f %f\n",out[i][0],out[i][1]);
    }

    return 0;
}

