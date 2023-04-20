#include<stdio.h>
#include<stdlib.h>
#include<malloc.h>
#include"lib.h"
#include<math.h>
#include"matlib.h"

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
numSteps      = (simDuration/timeStep);
samplePerStep = (timeStep/samplePeriod);
int codeLength=1023;
double sampleCount = (int)(sampleRate/(codeFreqBasis/codeLength));
int sc;
sc=(int)sampleCount;
int **codeTable;
codeTable=createMatint(14,10230);
codeTable=genNavicCatable(sampleRate);



return 0;
}
