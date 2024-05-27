#include <stdio.h>
#include<stdlib.h>
#include<math.h>


typedef struct 
{
    double real;
    double imag;
} Complex;

void fft(Complex* x,unsigned int size)
{
    // DFT
    unsigned int N = size, k = N, n;
    double thetaT = 3.14159265358979323846264338328 / N;
    Complex phiT = { cos(thetaT), -sin(thetaT) }, T;
    while (k > 1)
    {
        n = k;
        k >>= 1;
        phiT = (Complex){ phiT.real * phiT.real - phiT.imag * phiT.imag, 2 * phiT.real * phiT.imag };
        T = (Complex){ 1.0, 0.0 };
        for (unsigned int l = 0; l < k; l++)
        {
            for (unsigned int a = l; a < N; a += n)
            {
                unsigned int b = a + k;
                Complex t = { x[a].real - x[b].real, x[a].imag - x[b].imag };
                x[a] = (Complex){ x[a].real + x[b].real, x[a].imag + x[b].imag };
                x[b] = (Complex){ t.real * T.real - t.imag * T.imag, t.real * T.imag + t.imag * T.real };
            }
            T = (Complex){ T.real * phiT.real - T.imag * phiT.imag, T.real * phiT.imag + T.imag * phiT.real };
        }
    }

    // Decimate
    unsigned int m = (unsigned int)log2(N);
    for (unsigned int a = 0; a < N; a++)
    {
        unsigned int b = a;
        // Reverse bits
        b = (((b & 0xaaaaaaaa) >> 1) | ((b & 0x55555555) << 1));
        b = (((b & 0xcccccccc) >> 2) | ((b & 0x33333333) << 2));
        b = (((b & 0xf0f0f0f0) >> 4) | ((b & 0x0f0f0f0f) << 4));
        b = (((b & 0xff00ff00) >> 8) | ((b & 0x00ff00ff) << 8));
        b = ((b >> 16) | (b << 16)) >> (32 - m);
        if (b > a)
        {
            Complex t = x[a];
            x[a] = x[b];
            x[b] = t;
        }
    }

}



int main()
{
    Complex a[2048];
    int i;
    for(i=0;i<2048;i++)
    {
        a[i].real = i;
        a[i].imag = i;
    }

     for(i=0;i<20;i++)
    {
        printf("%lf+i%lf ",a[i].real,a[i].imag);
    }

    printf("\n \n ");

    fft(a,2048);

    for(i=0;i<20;i++)
    {
        printf("%lf+i%lf ",a[i].real,a[i].imag);
    }
    printf("\n \n ");

    fft(a,2048);

    for(i=0;i<2048;i++)
    {
        printf(" %lf+i%lf ",a[i].real/2048,a[i].imag/2048);
    }






}