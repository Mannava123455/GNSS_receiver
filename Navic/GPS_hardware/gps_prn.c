#include<stdio.h>
#include<stdlib.h>
#include<malloc.h>
#include<math.h>
#include<malloc.h>
#include"lib.h"

typedef struct {
    double real;
    double imag;
} Complex;

int shift(int *reg,int lr,int *fb,int lfb,int *output,int lo)
{
	int *out;
	out=(int *)malloc(lo*sizeof(int));
	int i;
	for(i=0;i<lo;i++)
	{
		out[i]=reg[output[i]-1];
	}
	int res;
	if(lo>1)
	{
		res=out[0]^out[1];
	}
	else
	{
		res=out[0];
	}
	int f;
	int *temp;
	temp=(int *)malloc(lfb*sizeof(int));
	for(i=0;i<lfb;i++)
	{
		temp[i]=reg[fb[i]-1];
	}
	int sum=0;
	for(i=0;i<lfb;i++)
	{
		sum=sum+temp[i];
	}
	f=sum%2;
	for (i=9;i>0;i--) 
	{
		reg[i]=reg[i-1];
	}
	reg[0]=f;
	return res;
}



int *PRN(int x)
{
	int sv[32][2]={{2,6},{3,7},{4,8},{5,9},{1,9},{2,10},{1,8},{2,9},{3,10},{2,3},{3,4},{5,6},{6,7},{7,8},{8,9},{9,10},{1,4},{2,5},{3,6},{4,7},{5,8},{6,9},{1,3},{4,6},{5,7},{6,8},{7,9},{8,10},{1,6},{2,7},{3,8},{4,9}};

	int *G1,*G2;
	G1=(int *)malloc(10*sizeof(int));
	G2=(int *)malloc(10*sizeof(int));
	int i;
	for(i=0;i<10;i++)
	{
		G1[i]=1;
	}
	for(i=0;i<10;i++)
	{
		G2[i]=1;
	}

	int *ca;
	ca=(int *) malloc(1023*sizeof(int));
	int g1,g2;

	int *fb1;
	int *output1;
	fb1=(int *)malloc(2*sizeof(int));
	output1=(int *)malloc(1*sizeof(int));
	output1[0]=10;
	fb1[0]=3;
	fb1[1]=10;

	int *d;
	d=(int *)malloc(2*sizeof(int));
	d[0]=sv[x][0];
	d[1]=sv[x][1];
	int *fb2;
	int *output2;
	fb2=(int *)malloc(6*sizeof(int));
	output2=(int *)malloc(2*sizeof(int));
	output2[0]=d[0];
	output2[1]=d[1];
	fb2[0]=2;
	fb2[1]=3;
	fb2[2]=6;
	fb2[3]=8;
	fb2[4]=9;
	fb2[5]=10;

	for(i=0;i<1023;i++)
	{
		g1=shift(G1,10,fb1,2,output1,1);
		g2=shift(G2,10,fb2,6,output2,2);
		ca[i]=(g1+g2)%2;
	}

	return ca;
}




int **genGPSCatable(double samplingFreq)
{
	int prnIdMax=32;
	int i,j;
	int codeLength=1023;
	double codeFreq=1.023*pow(10,6);
	double samplingPeriod=1/samplingFreq;
	double sampleCount = (int)(samplingFreq/(codeFreq/codeLength));
	int sc;
	sc=(int)sampleCount;
	int *r;
	r=(int *)malloc(sc*sizeof(int));
	r=arange(0,sc,1);
	for(i=0;i<sc;i++)
	{
		r[i]=r[i]*codeFreq*samplingPeriod;
	}
	int **table;
	table=createMatint(prnIdMax,codeLength);
	for(i=0;i<prnIdMax;i++)
	{
		int *dummy=PRN(i);
		for(j=0;j<codeLength;j++)
		{
			table[i][j]=dummy[j];
		}
		free(dummy);
	}

	int ** codeTable1;
	codeTable1=createMatint(prnIdMax,sc);
	for(i=0;i<prnIdMax;i++)
	{
		for(j=0;j<sc;j++)
		{
			codeTable1[i][j]=table[i][r[j]];
		}
	}
	int **codeTable;
	codeTable=createMatint(sc,prnIdMax);
	codeTable=transposeint(codeTable1,prnIdMax,sc);
	return codeTable;	
}



void fft(Complex* x, unsigned int size)
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

    //// Normalize (This section makes it not work correctly)
    // Complex f = { 1.0 / sqrt(N), 0.0 };
    // for (unsigned int i = 0; i < N; i++)
    //     x[i] = (Complex){ x[i].real * f.real, x[i].imag * f.imag };
}

void fftColumns(Complex* matrix, unsigned int rows, unsigned int cols) {
    Complex* column = (Complex*)malloc(rows * sizeof(Complex));
    for (unsigned int j = 0; j < cols; j++) {
        // Copy column data
        for (unsigned int i = 0; i < rows; i++) 
	{
            column[i] = matrix[i * cols + j];
        }
        fft(column, rows);
        for (unsigned int i = 0; i < rows; i++)
	{
            matrix[i * cols + j] = column[i];
        }
    }

    free(column);
}


int main()
{
	int prnIdMax=32;
	int i,j;
	int codeLength=1023;
	double codeFreq=1.023*pow(10,6);
	double samplingFreq=(2.048/1.023)*codeFreq;
	double samplingPeriod=1/samplingFreq;
	double sampleCount = (int)(samplingFreq/(codeFreq/codeLength));
	int sc;
	sc=(int)sampleCount;
	printf("%d\n",sc);
	int **codeTable;
	codeTable=createMatint(sc,prnIdMax);
	int *ca;
	codeTable=genGPSCatable(samplingFreq);
	pmfint("codeTable.dat",codeTable,sc,32);
	int **bpsk;
	bpsk=createMatint(sc,prnIdMax);
	for(i=0;i<sc;i++)
	{
		for(j=0;j<32;j++)
		{
			bpsk[i][j]=1-2*codeTable[i][j];
		}
	}
	double **fft_prn;
	fft_prn=createMat(sc,prnIdMax);
	  unsigned int rows = sc;
    unsigned int cols = 32;
	  Complex* matrix = (Complex*)malloc(rows * cols * sizeof(Complex));

    for (unsigned int i = 0; i < rows; i++)
    {
        for (unsigned int j = 0; j < cols; j++) 
	{
            matrix[i * cols + j].real=bpsk[i][j];

        }
    }

    // Perform FFT column-wise on the matrix
    fftColumns(matrix, rows, cols);

 for (unsigned int i = 0; i < rows; i++) 
 {
        for (unsigned int j = 0; j < cols; j++) 
	{
            printf("%lf+%lf ", matrix[i * cols + j].real, matrix[i * cols + j].imag);
        }
        printf(" \n");
    }


 double **temp1;
 temp1=createMat(rows,cols);
 double **temp2;
 temp2=createMat(rows,cols);
 for (unsigned int i = 0; i < rows; i++) 
 {
        for (unsigned int j = 0; j < cols; j++) 
	{
	temp1[i][j]=matrix[i*cols+j].real;

        }
    }
 for (unsigned int i = 0; i < rows; i++) 
 {
        for (unsigned int j = 0; j < cols; j++) 
	{
	temp2[i][j]=matrix[i*cols+j].imag;

        }
    }
	pmf("real.dat",temp1,rows,cols);
	pmf("imag.dat",temp2,rows,cols);




    // Cleanup
    free(matrix);
    return 0;

}






