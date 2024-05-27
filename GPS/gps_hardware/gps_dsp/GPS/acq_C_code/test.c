#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "iq_samples.h"


#define pi 3.14159265358979323846264338328
typedef struct 
{
    float real;
    float imag;
} Complex;

void g1_lfsr(unsigned char *out)
{
    int state = 0x3FF;
    int new_bit;
    int i;
    for(i=0;i<1023;i++)
    {
        if(i%8 == 0)
        {
            out[i/8] = 0x00;
        }
        out[i/8] |= ((state >> 9) & 0x1) << (7 - i%8);
        new_bit = ((state >> 9) ^ (state >> 2)) & 1;
        state = ((state << 1) | new_bit) & 0x3FF;
    }  
}

unsigned char *g2_lfsr(unsigned char tap0,unsigned char tap1)
{
    unsigned char *out;
    out = (unsigned char *)malloc(128);
    int state = 0x3FF;
    int new_bit;
    tap0--;
    tap1--;
    int i;
    for(i=0;i<1023;i++)
    {
         if(i%8 == 0)
        {
            out[i/8] = 0x00;
        }
        out[i/8] |= (((state >> tap0) ^ (state >> tap1)) & 0x1) << (7 - i%8);
        new_bit = ((state >> 9) ^ (state >> 8) ^ (state >> 7) ^ (state >> 5) ^ (state >> 2) ^ (state >> 1)) & 0x1;
        state = ((state << 1) | new_bit) & 0x3FF;
    }

    return out;
}

void combine_g1_and_g2(unsigned char * g1, unsigned char * g2, unsigned char * out) 
{
  int i;
  for (i = 0; i < 128; i++) 
  {
    out[i] = g1[i] ^ g2[i];
  }
}


/**** Function for computing fft *****/


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

    /* Declarations */

    int i,j,sv,k=0,tap1,tap2,p;
    int max_of_max;
    int doppler;
    int coh,non_coh;
    int max =0;
    int n;
    int max_index;
    int peak_to_noise_ratio;
    int max_of_max_index;
    int doppler_frequency;
    unsigned char *g1;
    unsigned char *g2;
    unsigned char *gold_code;
    int *bpsk;
    Complex upsampled_code[2048];
    Complex cossin[4096];
    Complex shifted_signal[4096];
    Complex signal_one_ms[2048];
    Complex mul_signal[2048];
    Complex coherent_product[2048];
    float non_coherent_product[2048];
    int start_index,end_index;
    float temp1,temp2;
    float sig_power[2048];

    int max_power[5] = {0};
    int visiblesatellites[5] = {0};
    int codephase[5] = {0};
    int frequencyoffset[5] ={0};
    unsigned char prn_codes[5][128];
    
  

    g1        = (unsigned char*)malloc(128);
    g2        = (unsigned char*)malloc(128);
    gold_code = (unsigned char*)malloc(128);
    bpsk      = (int *)malloc(1023*sizeof(int));


    g1_lfsr(g1);     /* Calling the function for g1_lfsr*/
    int *r;
    r=(int *)malloc(2048*sizeof(int));
    for(i=0;i<2048;i++)
    {
    	r[i]=i;
    }
    for(i=0;i<2048;i++)
    {
    	r[i]=r[i]*(1023.00/2048.00);
    }



    /* Main loop for all 32 satellites */

    for(sv = 0; sv <1; sv ++)
    {

        /* generating the prn code */
        tap1 = SVs[k++];
        tap2 = SVs[k++];
        g2 = g2_lfsr(tap1,tap2);
        combine_g1_and_g2(g1,g2,gold_code);


        /* BPSK modulation for prn code */

        p = 0;
        for(i=0;i<128;i++)
        {
            for(j=7;j>=0;j--)
            {
                if((gold_code[i] >> j) & 1)
                bpsk[p] = -1;
                else
                bpsk[p] = 1;
                if(p == 1022)
                {
                    break;
                }
                p++;
            }

        }


        /* upsample the prn code */

        /*for(i=0;i<1023;i++)
        {
            upsampled_code[2*i].real = bpsk[i];
            upsampled_code[2*i].imag = 0;
            upsampled_code[2*i+1].real = bpsk[i];
            upsampled_code[2*i+1].imag = 0;  
        }
        upsampled_code[2046].real = 0;
        upsampled_code[2046].imag = 0;
        upsampled_code[2047].real = 0;
        upsampled_code[2047].imag = 0;*/
	


	/* Upsample the prn code */

	for(i=0;i<2048;i++)
	{
		upsampled_code[i].real = bpsk[r[i]];
		upsampled_code[i].imag = 0;
	}
	for(i=0;i<2048;i++)
	{
		printf("%f, ",upsampled_code[i].real);
	}

	printf("\n");


        /** Compute FFT for upsampled_prn code ***/
        fft(upsampled_code,2048);
	for(i=0;i<2048;i++)
	{
		printf("%f + i%f \n, ",upsampled_code[i].real,upsampled_code[i].imag);
	}


        
        max_of_max = 0;

        for(doppler = -25000;doppler <= 25000; doppler=doppler + 500)
        {

            /** Computing e^-j2pifct  ****/
            for(i=0;i<4096;i++)
            {
                cossin[i].real = cos(2*pi*doppler*i/2048000);
                cossin[i].imag = sin(2*pi*doppler*i/2048000);
            }

            /**** Computing x[n]e^-j2pifct *****/
            for(i=0;i<4096;i++)
            {
                shifted_signal[i].real = (i_samples[i]*cossin[i].real + q_samples[i]*cossin[i].imag);
                shifted_signal[i].imag = (q_samples[i]*cossin[i].real - i_samples[i]*cossin[i].imag);
            }

            for(i=0;i<2048;i++)
            {
                non_coherent_product[i] = 0;
            }

            start_index = 0;
            end_index = start_index + 2048;

            /* Non coherent loop starts*/

            for(non_coh = 0; non_coh<1; non_coh++)
            {
                
                for(i=0;i<2048;i++)
                {
                    coherent_product[i].real = 0;
                    coherent_product[i].imag = 0;
                }

                /*Coherent loop starts*/

                for(coh = 0;coh<2;coh++)
                {
                    int z = 0;
                    for(i=start_index;i<end_index;i++)
                    {
                        signal_one_ms[z].real = shifted_signal[i].real;
                        signal_one_ms[z].imag = shifted_signal[i].imag;
                        z++;
                    }

                    /* FFT of 1msec signal */

                    fft(signal_one_ms,2048);

                    /*Multiply the signal with fft of prn code*/

                    for(i=0;i<2048;i++)
                    {
                        mul_signal[i].real =  (signal_one_ms[i].real*upsampled_code[i].real  +  signal_one_ms[i].imag*upsampled_code[i].imag);
                        mul_signal[i].imag =  (signal_one_ms[i].real*upsampled_code[i].imag  -  signal_one_ms[i].imag*upsampled_code[i].real);
                    }

                    /* Add to coherent array*/

                    for(i=0;i<2048;i++)
                    {
                        coherent_product[i].real = coherent_product[i].real + mul_signal[i].real;
                        coherent_product[i].imag = coherent_product[i].imag + mul_signal[i].imag;
                    }

                    start_index = start_index + 2048;
                    end_index = end_index + 2048;
                }

                /** Compute IFFT of the coherent product ***/

                fft(coherent_product,2048);

                for(i=1;i<1024;i++)
                {
                    temp1 = coherent_product[2048-i].real;
                    coherent_product[2048 - i].real = coherent_product[i].real;
                    coherent_product[i].real = temp1;

                    temp2 = coherent_product[2048-i].imag;
                    coherent_product[2048 - i].imag = coherent_product[i].imag;
                    coherent_product[i].imag = temp2;
                }


                for(i=0;i<2048;i++)
                {
                    coherent_product[i].real = coherent_product[i].real/2048;
                    coherent_product[i].imag = coherent_product[i].imag/2048;

                }

                for(i=0;i<2048;i++)
                {
                    sig_power[i] = coherent_product[i].real * coherent_product[i].real +  coherent_product[i].imag * coherent_product[i].imag;  
                }

                for(i=0;i<2048;i++)
                {
                    non_coherent_product[i] =  non_coherent_product[i] + sig_power[i];
                }

		max = 0;
		max_index = 0;

                for(i = 0;i<2048;i++)
                {
                    if(non_coherent_product[i] > max)
                    {
                        max = non_coherent_product[i];
                        max_index = i;
                    }
                }

                for(i=-2;i<3;i++)
                {
                    int index = (max_index + i + 2048)%2048;
                    non_coherent_product[index] = 0;
                }

                int noise = 0;
                for(i=0;i<2048;i++)
                {
                    noise = noise + (non_coherent_product[i])/(2048-5);
                }

                peak_to_noise_ratio = max/noise;

            }

            if(peak_to_noise_ratio > max_of_max)
            {
                max_of_max = peak_to_noise_ratio;
                max_of_max_index = max_index;
                doppler_frequency = doppler;
            }

        }


        for(i=0;i<5;i++)
        {

            if(max_of_max > max_power[i])
            {
                for(j=4;j>i;j--)
                {
                    max_power[j] = max_power[j-1];
                    visiblesatellites[j] = visiblesatellites[j-1];
                    codephase[j] = codephase[j-1];
                    frequencyoffset[j] = frequencyoffset[j-1];
                }

                max_power[i] = max_of_max;
                visiblesatellites[i] = sv;
                codephase[i] = max_of_max_index;
                frequencyoffset[i] = doppler_frequency;
                for(n=0;n<2048;n++)
                {
                    prn_codes[i][n] = gold_code[n];
                }

                break;
            }

        }

    }



    for(i=0;i<5;i++)
    {
        printf("sat = %d  doppler = %d codephase = %d \n",visiblesatellites[i]+1,frequencyoffset[i],codephase[i]);
    }

    
   return 0;







    


}
