#include<stdio.h>
#include<stdlib.h>
#include<malloc.h>
#include"lib.h"
#include<math.h>
#include"matlib.h"
#include<fftw3.h>
#include<complex.h>

int main()
{


// simulation constants
double codeFreqBasis,sampleRate,samplePeriod,simDuration,timeStep,numSteps,samplePerStep;

int prnidmax=14;

codeFreqBasis = 1.023*pow(10,6);
sampleRate    = 10*codeFreqBasis;
samplePeriod  = 1/sampleRate;
simDuration   = 1;
timeStep      = pow(10,-3);
numSteps      = (int)(simDuration/timeStep);
samplePerStep = (int)(timeStep/samplePeriod);

int codeLength=1023;
double sampleCount = (int)(sampleRate/(codeFreqBasis/codeLength));
int sc;
sc=(int)sampleCount;
int **codeTable;
codeTable=createMatint(sc,14);
codeTable=genNavicCatable(sampleRate);   // sampled prn sequence
pmfint("codetable.dat",codeTable,sc,14);  // saving the codetable in file

int satId[14]={5,7,3,1};
int numChannel = 4;
double c= 299792458;
double fe=1176.45e6;
double Dt=12;
double DtLin=10*log10(Dt);
double Dr=4;
double DrLin = 10*log10(Dr);
double Pt=44.8;
double k=1.380649e-23;
double T=300;
double rxBW = 24e6;
double Nr=k*T*rxBW;
double PLLIntegrationTime = 1e-3;
double PLLNoiseBandwidth  = 90;
double FLLNoiseBandwidth  = 4;
double DLLNoiseBandwidth  = 1;

// creating the imaginary matrix that contains the received signal
double *received_real,*received_imag,**received,**rfft;
received_real=createarr(sc);
received_imag=createarr(sc);
received_real=loadtxta("real.txt",sc);
received_imag=loadtxta("imag.txt",sc);
received=receivedsignal(received_real,received_imag,sc);  //received signal from transmitter


double fMin,fMax,fStep;
fMin=-5000;
fMax=5000;
fStep=500;
double *fSearch;
double length=(fMax-fMin)/fStep;
fSearch=createarr(length);
int i;
for(i=fMin;i<fMax+fStep;i=i+fStep)
{
	fSearch[i]=i;
}






















return 0;
}
