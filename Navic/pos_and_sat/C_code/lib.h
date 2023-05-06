#include<stdio.h>
#include<stdlib.h>
#include<malloc.h>
#include<math.h>
#include<complex.h>
#include<fftw3.h>
#include<malloc.h>

#define PI 3.141592653589793



double **createMat(int m,int n);
double *loadtxta(char *str,int m);
int **createMatint(int m,int n);
int **transposeint(int **a,  int m, int n);
int len(double *arr); 
double complex **createMat_complex(int m,int n);
int *genNavicCaCode(int s);
int **genNavicCatable(double samplingFreq);
int *arange(int m,int n,int step);
double **receivedsignal(double *a,double *b,int sc);
double complex *fft_complex(double **x, int n);
double complex *fft_real(double *x, int n);
double complex *fft(double complex *x, int n);
double complex *ifft(double complex *x, int n);
double complex **fft2d(double complex **in, int nrow, int ncol); 
double complex **ifft2d(double complex **in, int nrow, int ncol); 
void pmfint(char *str, int **a,int r,int c); 
void pmf(char *str, double **a,int r,int c);
void pmfarr(char *str,double *a,int sc); 
int *acquisition(double **x,int **prnSeq,int index,double fs,double *fSearch,int length,int threshold,int sc);


int **createMatint(int m,int n)
{
 int i;
 int **a;
 
 //Allocate memory to the pointer
a = (int **)malloc(m * sizeof( *a));
    for (i=0; i<m; i++)
         a[i] = (int *)malloc(n * sizeof( *a[i]));

 return a;
}



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

double complex  **createMat_complex(int m,int n)
{
 int i;
 double complex **a;
 
 //Allocate memory to the pointer
a = (double complex **)malloc(m * sizeof( *a));
    for (i=0; i<m; i++)
         a[i] = (double complex *)malloc(n * sizeof( *a[i]));

 return a;
}


int **transposeint(int **a,  int m, int n)
{
int i, j;
int **c;
//printf("I am here");
c = createMatint(n,m);

 for(i=0;i<n;i++)
 {
  for(j=0;j<m;j++)
  {
c[i][j]= a[j][i];
//  printf("%lf ",c[i][j]);
  }
 }
return c;

}

double **transpose(double **a,  int m, int n)
{
int i, j;
double **c;
//printf("I am here");
c = createMat(n,m);

 for(i=0;i<n;i++)
 {
  for(j=0;j<m;j++)
  {
c[i][j]= a[j][i];
  }
 }
return c;

}
int *arange(int m,int n,int step)
{
	int *a;
	a=(int*)malloc(n*sizeof(int));
	int i;
	for(i=m;i<n;i=i+step)
	{
		a[i]=i;
	}
	return a;
}


int len(double *arr) 
{
    int length = 0;
    while (*arr) 
    { 
        length++;
        arr++;
    }
    return length;
}


double *loadtxta(char *str,int m)
{

FILE *fp;
double *a;
int i;
a=(double*)malloc(m*sizeof(double));
fp = fopen(str, "r");
for(i=0;i<m;i++)
{
fscanf(fp,"%lf",&a[i]);
}
fclose(fp);
return a;

}

void pmf(char *str, double **a,int r,int c)  
{
int i,j;
FILE *fp;
fp = fopen(str,"w");
for (i = 0; i < r; i++)
{
for(j=0;j<c;j++)
{
fprintf(fp,"%lf ",a[i][j]);
}
fprintf(fp,"\n");
}
}



void pmfint(char *str, int **a,int r,int c)  
{
int i,j;
FILE *fp;
fp = fopen(str,"w");
for (i = 0; i < r; i++)
{
for(j=0;j<c;j++)
{
fprintf(fp,"%d ",a[i][j]);
}
fprintf(fp,"\n");
}
}


void pmfarr(char *str,double *a,int sc)  
{
FILE *fp;
fp = fopen(str,"w");
int i;
for(i=0;i<sc;i++)
{
fprintf(fp,"%lf\n",a[i]);
}
}



int *genNavicCaCode(int s)
{

int i,j;
int L5[28][10]={{1,1,1,0,1,0,0,1,1,1},
	    {0,0,0,0,1,0,0,1,1,0},
	    {1,0,0,0,1,1,0,1,0,0},
	    {0,1,0,1,1,1,0,0,1,0},
	    {1,1,1,0,1,1,0,0,0,0},
	    {0,0,0,1,1,0,1,0,1,1},
	    {0,0,0,0,0,1,0,1,0,0},
	    {0,1,0,0,1,1,0,0,0,0},
	    {0,0,1,0,0,1,1,0,0,0},
	    {1,1,0,1,1,0,0,1,0,0},
	    {0,0,0,1,0,0,1,1,0,0},
	    {1,1,0,1,1,1,1,1,0,0},
	    {1,0,1,1,0,1,0,0,1,0},
	    {0,1,1,1,1,0,1,0,1,0},
	    {0,0,1,1,1,0,1,1,1,1},
	    {0,1,0,1,1,1,1,1,0,1},
	    {1,0,0,0,1,1,0,0,0,1},
	    {0,0,1,0,1,0,1,0,1,1},
	    {1,0,1,0,0,1,0,0,0,1},
	    {0,1,0,0,1,0,1,1,0,0},
	    {0,0,1,0,0,0,1,1,1,0},
	    {0,1,0,0,1,0,0,1,1,0},
	    {1,1,0,0,0,0,1,1,1,0},
	    {1,0,1,0,1,1,1,1,1,0},
	    {1,1,1,0,0,1,0,0,0,1},
	    {1,1,0,1,1,0,1,0,0,1},
	    {0,1,0,1,0,0,0,1,0,1},
	    {0,1,0,0,0,0,1,1,0,1}};

int G1[10],G2[10],c1[1024],c2[1024];
int *CA;
int *a;
CA=(int *)malloc(1024*sizeof(int));
a=(int*)malloc(1*sizeof(int));
a[0]=1;

for(i=0;i<10;i++)
{
	G1[i] = 1;
}
if (s<0 || s>28)
{
	return a;
}
else if (s<28)
{
for(i=0;i<10;i++)
{
G2[i] = L5[s][i];
}
}

int k, temp;
for(k=0;k<1024;k++)
{
c1[k]=G1[9];
temp = G1[2]^G1[9];;
for (i = 9; i > 0; i--) 
{
G1[i] = G1[i - 1];    
}
G1[0] = temp;
}


for(k=0;k<1024;k++)
{
c2[k]=G2[9];
temp = G2[1]^G2[2]^G2[5]^G2[7]^G2[8]^G2[9];
for (i = 9; i > 0; i--) 
{
G2[i] = G2[i - 1];    
}

G2[0] = temp;
}


for(j=0;j<1023;j++)
{
CA[j]=c1[j]^c2[j];
}

return CA;
}



int **genNavicCatable(double samplingFreq)
{
	int prnIdMax=14;
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
		int *dummy=genNavicCaCode(i);
		for(j=0;j<codeLength;j++)
		{
			table[i][j]=dummy[j];
		}
		free(dummy);
	}

	int ** codeTable1;
	codeTable1=createMatint(14,10230);
	for(i=0;i<14;i++)
	{
		for(j=0;j<10230;j++)
		{
			codeTable1[i][j]=table[i][r[j]];
		}
	}
	int **codeTable;
	codeTable=createMatint(10230,14);
	codeTable=transposeint(codeTable1,14,10230);
	return codeTable;	
}



double **receivedsignal(double *a,double *b,int sc)
{
	int i,j;
	double **c;
	c=createMat(sc,2);
	for(i=0;i<sc;i++)
	{
		c[i][0]=a[i];
	}
	for(i=0;i<sc;i++)
	{
		c[i][1]=b[i];
	}

	return c;
}





// function for performing FFT of input signal and gives the output as double complex array.



double complex *fft_complex(double **x, int n)
{
    fftw_complex *in,*out;
    fftw_plan p;
    int i;
    in = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * n);
    for(i=0;i<n;i++)
    {
	    in[i][0]=x[i][0];
	    in[i][1]=x[i][1];
    }
    out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * n);
    p = fftw_plan_dft_1d(n, in, out, FFTW_FORWARD, FFTW_ESTIMATE);
    double complex *b;
    b=(double complex*)malloc(n*sizeof(double complex));
    fftw_execute(p);

    for(i=0;i<n;i++)
    {
	    b[i]=out[i][0] + out[i][1]*I;
    }

    fftw_destroy_plan(p);
    return b;
}


double complex *fft_real(double *x, int n)
{
    fftw_complex *in,*out;
    fftw_plan p;
    int i;
    in = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * n);
    for(i=0;i<n;i++)
    {
	    in[i][0]=x[i];
	    in[i][1]=0;
    }
    out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * n);
    p = fftw_plan_dft_1d(n, in, out, FFTW_FORWARD, FFTW_ESTIMATE);
    double complex *b;
    b=(double complex*)malloc(n*sizeof(double complex));
    fftw_execute(p);

    for(i=0;i<n;i++)
    {
	    b[i]=out[i][0] + out[i][1]*I;
    }

    fftw_destroy_plan(p);
    return b;
}

double complex *fft(double complex *x, int n)
{
    fftw_complex *in,*out;
    fftw_plan p;
    int i;
    in = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * n);
    for(i=0;i<n;i++)
    {
	    in[i][0]=creal(x[i]);
	    in[i][1]=cimag(x[i]);
    }
    out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * n);
    p = fftw_plan_dft_1d(n, in, out, FFTW_FORWARD, FFTW_ESTIMATE);
    double complex *b;
    b=(double complex*)malloc(n*sizeof(double complex));
    fftw_execute(p);

    for(i=0;i<n;i++)
    {
	    b[i]=out[i][0] + out[i][1]*I;
    }

    fftw_destroy_plan(p);
    return b;
}

double complex *ifft(double complex *x, int n)
{
    fftw_complex *in,*out;
    fftw_plan p;
    int i;
    in = (fftw_complex*)fftw_malloc(sizeof(fftw_complex) * n);
    for(i=0;i<n;i++)
    {
	    in[i][0]=creal(x[i]);
	    in[i][1]=cimag(x[i]);
    }
    out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * n);
    p = fftw_plan_dft_1d(n, in, out, FFTW_BACKWARD, FFTW_ESTIMATE);
    double complex *b;
    b=(double complex*)malloc(n*sizeof(double complex));
    fftw_execute(p);

    for(i=0;i<n;i++)
    {
	    b[i]=out[i][0] + out[i][1]*I;
    }

    fftw_destroy_plan(p);
    return b;
}

//function for performing fft for 2d matrix


double complex **fft2d(double complex **in, int nrow, int ncol) 
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

        fftw_execute(plan_forward);

        for(int j = 0; j < ncol; j++) 
	{
            out[i][j] = out_row[j][0] + out_row[j][1] * I;
        }
    }

    // Free memory and destroy plans
    fftw_destroy_plan(plan_forward);
    fftw_destroy_plan(plan_backward);
    fftw_free(in_row);
    fftw_free(out_row);
    return out; 
}


double complex **ifft2d(double complex **in, int nrow, int ncol) 
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
            out[i][j] = (out_row[j][0] + out_row[j][1]*I)/ncol;
        }
    }

    // Free memory and destroy plans
    fftw_destroy_plan(plan_forward);
    fftw_destroy_plan(plan_backward);
    fftw_free(in_row);
    fftw_free(out_row);
    return out; 
}

int *max(double **a,int m,int n)
{
    double max = a[0][0];
    int max_i = 0;
    int max_j = 0;

    for (int i = 0; i < m; i++) 
{
        for (int j = 0; j < n; j++) 
	{
            if (a[i][j] > max) 
	    {
                max = a[i][j];
                max_i = i;
                max_j = j;
            }
        }
    }
int *b;
b=(int*)malloc(2*sizeof(int));
b[0]=max_i;
b[1]=max_j;
return b;
}





	






int *acquisition(double **x,int **prnSeq,int index,double fs,double *fSearch,int length,int threshold,int sc)
{
	/* x is input signal 2d array containg sc rows and 2 cols  one col is real part and another one is imaginary part
	 * prnSeq is codeTable contains 14 cols and sc rows 
	 * index is integer selecting the particular column in codeTable
	 * fs is Sampling frequency
	 * fSearch is the array of frequencies to search for doppler frequency
	 * length is length of fSearch array
	 * Threshold is the value at max correlation
	 * sc is sample count
	 */
	   
	int i,j;
	threshold=0;

	//declarations 
	double *bpsk;   // 1-2*prnseq
	double complex *prnSeqfft;   //fft of prnseq
	double complex *cprnSeqfft;  //conjugate of fft of prnseq
	double ts=1/fs;
	int *t;
	double *a;
	double complex **signal;
	double complex *input;
	double complex **shift_input;
	double complex **XFFT;
	double complex **YFFT;
	double complex **IYFFT;
	double complex **Rxd;
	double **res;
	double **result;
	double *temp;
	double powIn;
	double s=0;
	double sMax;
	double thresholdEst;
	int *final,tau,fDev;




	//creations
	bpsk=(double *)malloc(sc*sizeof(double *));
	prnSeqfft=(double complex*)malloc(sc*sizeof(double complex));
	cprnSeqfft=(double complex*)malloc(sc*sizeof(double complex));
	a=(double *)malloc(sc*sizeof(double *));
	signal=createMat_complex(length,sc);
	input=(double complex*)malloc(sc*sizeof(double complex));
	shift_input=createMat_complex(length,sc);
	YFFT=createMat_complex(length,sc);
	IYFFT=createMat_complex(length,sc);
	Rxd=createMat_complex(length,sc);
	res=createMat(length,sc);
	temp=(double *)malloc(sc*sizeof(double));
	final=(int *)malloc(3*sizeof(int));


	for(i=0;i<sc;i++)
	{
		bpsk[i]=1-2*prnSeq[i][index];
	}
	prnSeqfft=fft_real(bpsk,sc);
	for(i=0;i<sc;i++)
	{
		cprnSeqfft[i]=conj(prnSeqfft[i]);
	}
	t=arange(0,sc,1);
	for(i=0;i<sc;i++)
	{
		a[i]=t[i]*ts;
	}
	for(i=0;i<sc;i++)
	{
		input[i]=x[i][0] + x[i][1]*I;
	}
	for(i=0;i<length;i++)
	{
		for(j=0;j<sc;j++)
		{
			signal[i][j]=cexp(-2*I*PI*fSearch[i]*a[j]);
		}
	}
	for(i=0;i<length;i++)
	{
		for(j=0;j<sc;j++)
		{
			shift_input[i][j]=input[j]*signal[i][j];
		}
	}
	XFFT=fft2d(shift_input,length,sc);
	for(i=0;i<length;i++)
	{
		for(j=0;j<sc;j++)
		{
			YFFT[i][j]=XFFT[i][j]*cprnSeqfft[j];
		}
	}
	IYFFT=ifft2d(YFFT,length,sc);
	for(i=0;i<length;i++)
	{
		for(j=0;j<sc;j++)
		{
			Rxd[i][j]=IYFFT[i][j]/sc;
		}
	}
	for(i=0;i<length;i++)
	{
		for(j=0;j<sc;j++)
		{
			res[i][j]=pow(cabs(Rxd[i][j]),2);
		}
	}
	result=transpose(res,length,sc);

	int *b;
	b=(int *)malloc(2*sizeof(int));
	b=max(result,sc,length);
	for(j=0;j<sc;j++)
	{
		temp[j]=pow(cabs(input[j]),2);
	}
	for(j=0;j<sc;j++)
	{
		s=s+temp[j];
	}
	powIn=s/sc;
	sMax=result[b[0]][b[1]];
	thresholdEst=2*sc*sMax/powIn;
	if(thresholdEst>threshold)
	{
		tau=b[0];
		fDev=fSearch[b[1]];
		final[0]=1;
		final[1]=tau;
		final[2]=fDev;
		return b;
	}
	else
	{
		return final;
	}



	
}

	











