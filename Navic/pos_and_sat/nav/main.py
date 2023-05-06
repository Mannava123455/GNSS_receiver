import numpy as np
import scipy.constants as sciconst
import matplotlib.pyplot as plt
import navicsim as navs


def navic_pcps_acquisition(x, prnSeq, fs, fSearch, threshold=0):

    prnSeqFFT = np.conjugate(np.fft.fft(1-2*prnSeq))
    
    K = x.shape[0]        #10230
    N = fSearch.shape[0]  #21
    ts = 1/fs
    t = np.arange(K)*ts

    Rxd = np.empty((K, N), dtype=np.complex_)
    for i in range(0,N):
        x_iq = x*np.exp(-1j*2*np.pi*fSearch[i]*t)
        XFFT = np.fft.fft(x_iq)
        YFFT = XFFT*prnSeqFFT
        Rxd[:,i] = (1/K)*np.fft.ifft(YFFT)
    np.savetxt("ds.dat",np.abs(Rxd)**2)

    maxIndex = np.argmax(np.abs(Rxd)**2)
    print(maxIndex)
    maxCol = maxIndex%N
    maxRow = maxIndex//N
    print(maxCol)
    print(maxRow)
    d=[]
    d=np.abs(Rxd)**2
    print(d[maxRow,maxCol])

    powIn = np.mean(np.abs(x)**2)
    sMax = np.abs(Rxd[maxRow, maxCol])**2
    thresholdEst = 2*K*sMax/powIn

    if(thresholdEst > threshold):
        tau = maxRow
        fDev = fSearch[maxCol]
        return True, tau, fDev
    else:
        return False, 0, 0


fMin = -5000
fMax = 5000
fStep = 500
fSearch = np.arange(fMin, fMax+fStep, fStep)
r=np.loadtxt("real.dat",dtype=float)
im=np.loadtxt("imag.dat",dtype=float)
waveform=r+im*1j
codeTable=np.loadtxt("codetable.dat")
sampleRate=10230
status, codePhase, doppler = navic_pcps_acquisition(
                                    waveform, 
                                    codeTable[np.arange(0, 10230)%10230, 4], 
                                    10230000, 
                                    fSearch
                                )   




