#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#include "fftw3.h"

#define MAX_LEN 16320

/******************************************
* Details of the space vehicles  
******************************************/
int SVs[] = { // PRN, Navstar, taps
     1,  63,  2,  6,
     2,  56,  3,  7,
     3,  37,  4,  8,
     4,  35,  5,  9,
     5,  64,  1,  9,
     6,  36,  2, 10,
     7,  62,  1,  8,
     8,  44,  2,  9,
     9,  33,  3, 10,
    10,  38,  2,  3,
    11,  46,  3,  4,
    12,  59,  5,  6,
    13,  43,  6,  7,
    14,  49,  7,  8,
    15,  60,  8,  9,
    16,  51,  9, 10,
    17,  57,  1,  4,
    18,  50,  2,  5,
    19,  54,  3,  6,
    20,  47,  4,  7,
    21,  52,  5,  8,
    22,  53,  6,  9,
    23,  55,  1,  3,
    24,  23,  4,  6,
    25,  24,  5,  7,
    26,  26,  6,  8,
    27,  27,  7,  9,
    28,  48,  8, 10,
    29,  61,  1,  6,
    30,  39,  2,  7,
    31,  58,  3,  8,
    32,  22,  4,  9,
};

/**********************************************************
* Structure to generate the C/A gold codes that are transmitted
* by each satellite. Combines the output of the G1 and G2
* LFSRs to produce the 1023 symbol sequence.
**********************************************************/
typedef struct {
    char g1[11];
    char g2[11];
    char* tap[2];
} CACODE;

void CACODE_init(CACODE* ca, int t0, int t1) {
    ca->tap[0] = ca->g2 + t0;
    ca->tap[1] = ca->g2 + t1;
    memset(ca->g1 + 1, 1, 10);
    memset(ca->g2 + 1, 1, 10);
}

int CACODE_Chip(CACODE* ca) {
    return ca->g1[10] ^ *ca->tap[0] ^ *ca->tap[1];
}

void CACODE_Clock(CACODE* ca) 
{
    ca->g1[0] = ca->g1[3] ^ ca->g1[10];
    ca->g2[0] = ca->g2[2] ^ ca->g2[3] ^ ca->g2[6] ^ ca->g2[8] ^ ca->g2[9] ^ ca->g2[10];
    memmove(ca->g1 + 1, ca->g1, 10);
    memmove(ca->g2 + 1, ca->g2, 10);
}




void readDataFiles(const char *iFile, const char *qFile, int a[][2], int *len) 

{
    FILE *fi, *fq;
    double x, y;
    int i = 0;

    fi = fopen(iFile, "r");
    if (fi == NULL) {
        perror("Error opening i.dat file");
        exit(1);
    }

    fq = fopen(qFile, "r");
    if (fq == NULL) {
        perror("Error opening q.dat file");
        fclose(fi);  
        exit(1);
    }

    while (fscanf(fi, "%lf", &x) != EOF && fscanf(fq, "%lf", &y) != EOF) {
        if (i < MAX_LEN) {
            a[i][0] = (int)x;
            a[i][1] = (int)y;
            i++;
        } else {
            break;
        }
    }

    *len = i;

    fclose(fi);
    fclose(fq);
}



int main(int argc, char* argv[])
{
    /****************************
    * Details of the input file
    ****************************/
    //const int fc = 4092000; // or 1364000
    const int fs = 2040000;
    const char* in = "gps.bin";
    const int ms = 8; // Length of data to process (milliseconds)
    const int Start = 0;
    int i;

    /**************************************
    * Derived values
    **************************************/
    const int Len = ms * fs / 1000;

    
    int a[MAX_LEN][2];
    int len;
    readDataFiles("i.dat","q.dat",a,&len);

    ///////////////////////////////////////////////////////////////////////////////////////////////

    fftw_complex* code = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * Len);
    fftw_complex* data = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * Len);
    fftw_complex* prod = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * Len);

    fftw_plan p;

    /***************************************
    * Read in the file. Data is
    * packed LSB first (sample 0 in bit 0)
    ****************************************/


    printf("PRN Nav Doppler   Phase   MaxSNR\n");
    /********************************************
    *  Process all space vehicles in turn
    ********************************************/
    int sv = 0;
    while (sv < sizeof(SVs) / sizeof(int)) {
        int PRN = SVs[sv++];
        int Navstar = SVs[sv++];
        int T1 = SVs[sv++];
        int T2 = SVs[sv++];

        if (!PRN) break;

        /*************************************************
        * Generate the C/A code for the window of the
        * data (at the sample rate used by the data stream
        *************************************************/

        CACODE ca;
        CACODE_init(&ca, T1, T2);

        double ca_freq = 1023000, ca_phase = 0, ca_rate = ca_freq / fs;

        for (i = 0; i < Len; i++) {
            code[i][0] = CACODE_Chip(&ca) ? -1 : 1;
            code[i][1] = 0;
            ca_phase += ca_rate;

            if (ca_phase >= 1) {
                ca_phase -= 1;
                CACODE_Clock(&ca);
            }
        }

        /******************************************
        * Now run the FFT on the C/A code stream  *
        ******************************************/
        p = fftw_plan_dft_1d(Len, code, code, FFTW_FORWARD, FFTW_ESTIMATE);
        fftw_execute(p);
        fftw_destroy_plan(p);

        /*************************************************
        * Now generate the same for the sample data, but
        * removing the Local Oscillator from the samples.
        *************************************************/


        for (i = 0; i < Len; i++) 
	{
            data[i][0] = a[i][0] ? -1 : 1;
            data[i][1] = a[i][1] ? -1 : 1;
        }

        p = fftw_plan_dft_1d(Len, data, data, FFTW_FORWARD, FFTW_ESTIMATE);
        fftw_execute(p);
        fftw_destroy_plan(p);

        /***********************************************
        * Generate the execution plan for the Inverse
        * FFT (which will be reused multiple times
        ***********************************************/

        p = fftw_plan_dft_1d(Len, prod, prod, FFTW_BACKWARD, FFTW_ESTIMATE);

        double max_snr = 0;
        int max_snr_dop, max_snr_i;

        /************************************************
        * Test at different doppler shifts (+/- 5kHz)
        ************************************************/
        for (int dop = -5000 * Len / fs; dop <= 5000 * Len / fs; dop++) 
	{
            double max_pwr = 0, tot_pwr = 0;
            int max_pwr_i;

            /*********************************************
            * Complex multiply the C/A code spectrum
            * with the spectrum that came from the data
            ********************************************/
            for (i = 0; i < Len; i++) {
                int j = (i - dop + Len) % Len;
                prod[i][0] = data[i][0] * code[j][0] + data[i][1] * code[j][1];
                prod[i][1] = data[i][0] * code[j][1] - data[i][1] * code[j][0];
            }

            /**********************************
            * Run the inverse FFT
            **********************************/
            fftw_execute(p);

            /*********************************
            * Look through the result to find
            * the point of max absolute power
            *********************************/
            for (i = 0; i < fs / 1000; i++) {
                double pwr = prod[i][0] * prod[i][0] + prod[i][1] * prod[i][1];
                if (pwr > max_pwr) max_pwr = pwr, max_pwr_i = i;
                tot_pwr += pwr;
            }
            /*****************************************
            * Normalize the units and find the maximum
            *****************************************/
            double ave_pwr = tot_pwr / i;
            double snr = max_pwr / ave_pwr;
            if (snr > max_snr) max_snr = snr, max_snr_dop = dop, max_snr_i = max_pwr_i;
        }
        fftw_destroy_plan(p);

        /*****************************************
        * Display the result
        *****************************************/
        printf("%-2d %4d %7.0f %8.1f %7.1f    ",
            PRN,
            Navstar,
            max_snr_dop * (double)(fs) / Len,
            (max_snr_i * 1023.0) / (fs / 1000),
            max_snr);

        for (i = (int)(max_snr) / 10; i--; ) putchar('*');
        putchar('\n');
    }

    fftw_free(code);
    fftw_free(data);
    fftw_free(prod);
    return 0;
}

