import numpy as np
import scipy.constants as sciconst
import matplotlib.pyplot as plt
import sim as navs

def navic_pcps_acquisition(x, prnSeq, fs,  threshold=0, relative_peak=False):

    """Performs PCPS (Parallel Code Phase Search) acquisition

    :param x: Input signal buffer
    :param prnSeq: Sampled PRN sequence of satellite being searched
    :param fs: Sampling rate
    :param fSearch: Array of Doppler frequencies to search
    :param threshold: Threshold value above which satellite is considered as visible/acquired, defaults to 0
    :return status, codeShift, dopplerShift: status is 'True' or 'False' for signal acquisition. In the case of staus being 'True', it provides coarse estimations of code phase and Doppler shift.
    """

    prnSeqFFT = np.conjugate(np.fft.fft(1-2*prnSeq))
    z=1
    K = x.shape[0]
    Rxd = np.empty(K)
    x_iq = x
    XFFT = np.fft.fft(x_iq)
    YFFT = XFFT*prnSeqFFT
    Rxd = np.abs((1/K)*np.fft.ifft(YFFT))**2
    for i in range(0,len(Rxd)):
        if Rxd[i] == max(Rxd):
            return i,max(Rxd)

codeFreqBasis = 1.023e6
sampleRate = 2.048e6
samplePeriod = 1/sampleRate

codeTable = navs.genGpsCaTable(sampleRate)
codeTableSampCnt = len(codeTable)
# [3 6 7 16 18 19 21 22 30]
satId = np.arange(1,32+1)
numChannel = len(satId)

acqIntegTime = 4e-3

PLLIntegrationTime = 1e-3
PLLNoiseBandwidth = 90 # In Hz
FLLNoiseBandwidth = 4  # In Hz
DLLNoiseBandwidth = 1  # In Hz


cevafile = "/home/mannava/gps_sdr/gps-sdr-sim/gpssim.bin"
data = np.fromfile(cevafile, dtype=np.int8)
data_I = data[0::2]; data_Q = data[1::2]
data = data_I + 1j*data_Q

simDuration = len(data)/sampleRate
timeStep = PLLIntegrationTime
numSteps = round(simDuration/timeStep)
samplePerStep = round(timeStep/samplePeriod)

print(simDuration, numSteps)


waveform = data[0:4096]
code = waveform[0:2048]     
maxi  = np.empty(33)
codephase=[]
# Perform acquisition for each satellite
for prnId in satId:


    
    status,maxi[prnId] = navic_pcps_acquisition(
                                            code, 
                                            codeTable[np.arange(0, 2048)%codeTableSampCnt, prnId-1], 
                                            sampleRate, 
                                            threshold=3,
                                            relative_peak=True
                                        )
    codephase.append(status)

    

d=maxi[1:]
l = sorted(range(len(d)), key=lambda k: d[k])
l = l[-4:]
l = [x+1 for x in l]
print(l)
delay=[]
for i in l:
    delay.append(codephase[i-1])
print(delay)



fMin = -5000
fMax = 5000
fStep = 200
fSearch = np.arange(fMin, fMax+fStep, fStep)
N = fSearch.shape[0]
fs = sampleRate
ts = 1/fs
t = np.arange(2048)*ts

freq = []
for i in range(0,4):
    prn    =  1-2*codeTable[np.arange(0, 2048)%codeTableSampCnt, l[i]-1]
    j_max = -1
    max_of_max = 0
    for j in range(0,N):
        code2  =  waveform[delay[i]:delay[i]+2048]
        x_iq = code2*np.exp(-1j*2*np.pi*fSearch[j]*t)
        result = np.abs(np.sum(x_iq*prn))**2
        if result > max_of_max:
            max_of_max = result
            j_max = j
    freq.append(fSearch[j_max])
    print(f"For sat={l[i]}, max_of_max occurred at doppler={fSearch[j_max]} with value {max_of_max}")
print(freq)
         


       

        
    







            