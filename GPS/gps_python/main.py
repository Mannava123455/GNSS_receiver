import numpy as np
import scipy.constants as sciconst
import matplotlib.pyplot as plt
import gpssim as navs

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


state = "ACQ"

for istep in range(numSteps):

    waveform = data[istep*samplePerStep: (istep+1)*samplePerStep]
    
    # Perform acquisition once from cold-start
    if (istep+1)*timeStep >= acqIntegTime and state == "ACQ":
        acqBuffer = data[0: (istep+1)*samplePerStep]
        acqBufferLen = len(acqBuffer)
        print(acqBufferLen)

        # Acqusition doppler search space
        fMin = -5000
        fMax = 5000
        fStep = 200
        fSearch = np.arange(fMin, fMax+fStep, fStep)

        tracker = []
        satVis = 0
        
        # Perform acquisition for each satellite
        for prnId in satId:
            status, codePhase, doppler, peakMetric = navs.navic_pcps_acquisition(
                                            acqBuffer, 
                                            codeTable[np.arange(0, acqBufferLen)%codeTableSampCnt, prnId-1], 
                                            sampleRate, 
                                            fSearch,
                                            threshold=3,
                                            relative_peak=True
                                        )   
            delaySamp = codePhase
            codePhase = (codePhase % codeTableSampCnt)/(sampleRate/codeFreqBasis)

            if(status):
                print(f"Acquisition results for PRN ID {prnId}\n Status:{status} Doppler:{doppler} Delay/Code-Phase:{delaySamp}/{codePhase} Peak-Metric:{peakMetric}")

            state = "TRK"

            # If a satellite is visible, initialize tracking loop
            if(status == True):
                satVis += 1

                tracker.append(navs.NavicTracker())
                tracker[-1].SampleRate = sampleRate
                tracker[-1].CenterFrequency = 0
                tracker[-1].PLLNoiseBandwidth = PLLNoiseBandwidth
                tracker[-1].FLLNoiseBandwidth = FLLNoiseBandwidth
                tracker[-1].DLLNoiseBandwidth = DLLNoiseBandwidth
                tracker[-1].PLLIntegrationTime = round(PLLIntegrationTime*1e3)
                tracker[-1].PRNID = prnId
                tracker[-1].InitialDopplerShift = doppler
                tracker[-1].InitialCodePhaseOffset = codePhase
                tracker[-1].setupImpl()
                tracker[-1].resetImpl()

            trackDataShape = (numSteps*round(PLLIntegrationTime*1e3), satVis)
            y = np.empty(trackDataShape, dtype=np.complex_)
            fqyerr = np.empty(trackDataShape)
            fqynco = np.empty(trackDataShape)
            pherr = np.empty(trackDataShape)
            phnco = np.empty(trackDataShape)
            delayerr = np.empty(trackDataShape)
            delaynco = np.empty(trackDataShape)

    # Perform tracking for visible satellites
    if(state == "TRK"):
        for i in range(satVis):
            y[istep, i], fqyerr[istep, i], fqynco[istep, i], pherr[istep, i], phnco[istep, i], delayerr[istep, i], delaynco[istep, i] = tracker[i].stepImpl(waveform)

for i in range(satVis):
    
    plt.subplot(6, 1, 1)
    plt.plot(fqyerr[:, i])
    plt.ylim(0,50)
    plt.xlabel('time')
    plt.ylabel('Fqy Error')
    

    plt.subplot(6, 1, 2)
    plt.plot(fqynco[:, i])
    plt.xlabel('time')
    plt.ylabel('Fqy NCO')

    plt.subplot(6, 1, 3)
    plt.plot(pherr[:, i])
    plt.xlabel('time')
    plt.ylabel('Phase Error')

    plt.subplot(6, 1, 4)
    plt.plot(phnco[:, i])
    plt.xlabel('time')
    plt.ylabel('Phase NCO')

    plt.subplot(6, 1, 5)
    plt.plot(delayerr[:, i])
    plt.xlabel('time')
    plt.ylabel('Delay Error')

    plt.subplot(6, 1, 6)
    plt.plot(delaynco[:, i])
    plt.xlabel('time')
    plt.ylabel('Delay NCO')
    plt.title(format(tracker[i].PRNID))
    plt.show()
        
for i in range(satVis):
    resultId = tracker[i].PRNID
    print(resultId)
    satIdx = list(satId).index(resultId)
    print(satIdx)

    mapbit = lambda y: np.piecewise(np.imag(y), [np.imag(y) < 0, np.imag(y) >= 0], [0, 1])
    mapbitinv = lambda y: np.piecewise(np.imag(y), [np.imag(y) < 0, np.imag(y) >= 0], [1, 0])

    print("Prompt I branch:\n", mapbit(y[:, i]))
    print("Prompt I branch inverted:\n", mapbitinv(y[:, i]))



    
