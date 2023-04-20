import numpy as np
import scipy.constants as sciconst
import matplotlib.pyplot as plt
import navicsim as navs
#code chip rate, sample rate and sample period
#refer to navicsim.py for all function detials
codeFreqBasis = 1.023e6
sampleRate = 10*codeFreqBasis
samplePeriod = 1/sampleRate

#simulation duration, steps at which values are recorded(here for every 1ms)
simDuration = 1
timeStep = 1e-3
numSteps = round(simDuration/timeStep)
samplePerStep = int(timeStep/samplePeriod)
codeTable = navs.genNavicCaTable(sampleRate)
print(codeTable)
np.savetxt("c.txt",codeTable)
codeTableSampCnt = len(codeTable)


#satId is the satellite ID for multiple satellites to track
satId = np.array([5, 7, 3, 1])
numChannel = len(satId)
c = sciconst.speed_of_light
fe = 1176.45e6;              
Dt = 12;                     
DtLin = 10*np.log10(Dt)
Dr = 4;                      
DrLin = 10*np.log10(Dr)
Pt = 44.8;                   
k = sciconst.Boltzmann;  
T = 300;                     
rxBW = 24e6;                 
Nr = k*T*rxBW;


#simulation constants for tracking loop
PLLIntegrationTime = 1e-3
PLLNoiseBandwidth = 90 # In Hz
FLLNoiseBandwidth = 4  # In Hz
DLLNoiseBandwidth = 1  # In Hz
#frequrency shift to be applied to the signal
fShift = np.array([3589, 2256, 1596, 2568])
channelpfo = navs.PhaseFrequencyOffset(sampleRate)
#sigDelay is the delay in samples in channels
sigDelay = np.array([300.34, 587.21, 425.89, 312.88])
dynamicDelayRange = 50


staticDelay = np.round(sigDelay - dynamicDelayRange)
channelstatd = navs.IntegerDelay(staticDelay)
channelvard = navs.FractionalDelay(4, 65535)

sqrtPr = np.sqrt(Pt*DtLin*DrLin)*(1/(4*np.pi*(fe+fShift)*sigDelay*samplePeriod))

datagen = navs.NavicDataGen(50, sampleRate, numChannel)
modulator = navs.NavicL5sModulator(sampleRate)

rms = lambda x: np.sqrt(np.mean(np.abs(x)**2, axis=0)) 


# Baseband modulation
navdata = datagen.GenerateBits(timeStep)
iqsig = modulator.Modulate(navdata, codeTable[:, satId-1])

# Doppler shift
doppsig = channelpfo.Offset(iqsig, fShift)

# Delay
staticDelayedSignal = channelstatd.Delay(doppsig)
leftoutDelay = sigDelay - staticDelay
delayedSig = channelvard.Delay(staticDelayedSignal, leftoutDelay)

# Power scaling
scaledSig = navs.PowerScale(delayedSig, sqrtPr)

# Add signals from each channel
resultsig = np.sum(scaledSig, axis=1)

# Generate noise
noisesig = (np.random.normal(scale=Nr**0.5, size=(samplePerStep, )) + 1j*np.random.normal(scale=Nr**0.5, size=(samplePerStep, )))/2**0.5

# Add thermal noise to composite signal
rxwaveform = resultsig + noisesig

# Scale received signal to have unit power
waveform = rxwaveform/rms(rxwaveform)
fMin = -5000
fMax = 5000
fStep = 500
fSearch = np.arange(fMin, fMax+fStep, fStep)
tracker = []
satVis = 0
        
        # Perform acquisition for each satellite
status, codePhase, doppler = navs.navic_pcps_acquisition(
                                    waveform, 
                                    codeTable[np.arange(0, samplePerStep)%codeTableSampCnt, 4], 
                                    sampleRate, 
                                    fSearch
                                )   
delaySamp = codePhase
codePhase = (codePhase % codeTableSampCnt)/(sampleRate/codeFreqBasis)

np.savetxt("TransmittedWave.txt",waveform)


