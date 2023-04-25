import numpy as np
from fractions import Fraction

# CA code generation API
#Initial condition of register G2 taken from NavIC ICD
SV_L5 = {
   1: '1110100111',
   2: '0000100110',
   3: '1000110100',
   4: '0101110010',
   5: '1110110000',
   6: '0001101011',
   7: '0000010100',
   8: '0100110000',
   9: '0010011000',
  10: '1101100100',
  11: '0001001100',
  12: '1101111100',
  13: '1011010010',
  14: '0111101010',
}


SV_S = {
   1: '0011101111',
   2: '0101111101',
   3: '1000110001',
   4: '0010101011',
   5: '1010010001',
   6: '0100101100',
   7: '0010001110',
   8: '0100100110',
   9: '1100001110',
  10: '1010111110',
  11: '1110010001',
  12: '1101101001',
  13: '0101000101',
  14: '0100001101',
}

#PRN code generation for NavIC constellation

#function to shift the bits according to taps given to registers
#function for LFSR 
def shift(register, feedback, output):
    """GPS Shift Register
    
    :param list feedback: which positions to use as feedback (1 indexed)
    :param list output: which positions are output (1 indexed)
    :returns output of shift register:
    
    """
    
    # calculate output
    out = [register[i-1] for i in output]
    if len(out) > 1:
        out = sum(out) % 2
    else:
        out = out[0]
        
    # modulo 2 add feedback
    fb = sum([register[i-1] for i in feedback]) % 2
    
    # shift to the right
    for i in reversed(range(len(register[1:]))):
        register[i+1] = register[i]
        
    # put feedback in position 1
    register[0] = fb
    
    return out

#function to generate the PRN sequrnce of size 1023 for given the satellite ID

def genNavicCaCode(sv):
    """Build the CA code (PRN) for a given satellite ID
    
    :param int sv: satellite code (1-14 L5 band, 15-28 S band)
    :returns list: ca code for chosen satellite
    
    """
    # init registers
    G1 = [1 for i in range(10)]

    if(sv<1 or sv>28):
        print("Error: PRN ID out of bounds!")
        return None
    elif(sv<14):
        G2 = [int(i) for i in [*SV_L5[sv]]]
    else:
        G2 = [int(i) for i in [*SV_S[sv]]]

    ca = [] # stuff output in here

    # create sequence
    codeLength = 1023
    for j in range(codeLength):
        g1 = shift(G1, [3,10], [10])
        g2 = shift(G2, [2,3,6,8,9,10], [10])
    
    # modulo 2 add and append to the code
        ca.append((g1 + g2) % 2)

    # return C/A code!
    return np.array(ca)

#function to upsample the PRN sequence generated to required sampling rate
# The below function will generate the samples of prn code for the given sample frequency

def genNavicCaTable(samplingFreq):
    prnIdMax = 14
    codeLength = 1023
    codeFreqBasis = 1.023e6
    samplingPeriod = 1/samplingFreq
    sampleCount = int(np.round(samplingFreq / (codeFreqBasis / codeLength)))
    indexArr = (np.arange(sampleCount)*samplingPeriod*codeFreqBasis).astype(np.float32)     # Avoid floating point error due to high precision
    indexArr = indexArr.astype(int)
    return np.array([genNavicCaCode(i) for i in range(1,prnIdMax+1)])[:,indexArr]#.T

# Bit generation and Modulation API
#class below will generate modulated IQ samples, follows ICD












class NavicL5sModulator():
    def __init__(self, fs):
        self.sampleRate = fs
        self.codePhase = 0
        self.subCarrPhase = 0

    # columns of x have samples
    # columns of codeTable have sampled PRN sequence
    def Modulate(self, x, codeTable):
        codeNumSample = codeTable.shape[0]
        numSample = x.shape[0]
        numChannel = x.shape[1]
        #BPSK modulation
        spsBpskSig = 1-2*np.logical_xor(x, codeTable[np.arange(self.codePhase, self.codePhase+numSample)%codeNumSample, :])

        subCarrFd = 2*5*1.023e6
        subCarrSym = np.array([1, -1])
        subCarr1Ch = subCarrSym[(np.arange(numSample)*subCarrFd/self.sampleRate + self.subCarrPhase).astype(np.int32) & 1]
        SubCarrSig = np.tile(np.array([subCarr1Ch]).T, (1, numChannel))
        PilotSig = np.ones((numSample, numChannel)); PilotSig[1::2, :] = -1
        DataSig = 1-2*np.random.binomial(1, 0.5, (numSample, numChannel))

        rsBocPilotSig = PilotSig * SubCarrSig
        rsBocDataSig = DataSig * SubCarrSig

        interplexSig = spsBpskSig * rsBocDataSig * rsBocPilotSig

        self.codePhase = (self.codePhase+numSample)%codeNumSample
        self.subCarrPhase += (numSample*subCarrFd/self.sampleRate)%1; self.subCarrPhase %= 1

        alpha = (2**0.5)/3
        beta = 2/3
        gamma = 1/3 
        # Document formula
        iqsig = alpha*(spsBpskSig + rsBocPilotSig) + 1j*(beta*rsBocDataSig - gamma*interplexSig)
        return iqsig

    def Release(self):
        self.codePhase = 0
        self.subCarrPhase = 0












#class to generate navigation data at 50sps
class NavicDataGen():
    def __init__(self, ds=50, fs=10*1.023e6, numChannel=1, file=None):
      self.dataRate = ds
      self.sampleRate = fs
      self.numSamplesPerBit = round(fs/ds)
      self.samplesToNextBit = self.numSamplesPerBit
      self.numChannel = numChannel
      self.bitStream = np.empty((1, numChannel))
      self.bitStream[0,:] = np.random.binomial(1, 0.5, (numChannel, ))

    def GenerateBits(self, timeInterval):
      genStream = np.empty((1,self.numChannel))
      numBitsToGen = round(self.sampleRate*timeInterval)

      bufferCnt = numBitsToGen
      while bufferCnt > 0:
        if(bufferCnt < self.samplesToNextBit):
          genStream = np.append(genStream, np.repeat(self.bitStream[-1:], bufferCnt, axis=0), axis=0)
          self.samplesToNextBit -= bufferCnt
          bufferCnt = -1
        else:
          genStream = np.append(genStream, np.repeat(self.bitStream[-1:], self.samplesToNextBit, axis=0), axis=0)
          self.bitStream = np.append(self.bitStream, np.random.binomial(1, 0.5, (1, self.numChannel)), axis=0)
          bufferCnt -= self.samplesToNextBit
          self.samplesToNextBit = self.numSamplesPerBit
      
      return genStream[1:numBitsToGen+1]
    
    def GetBitStream(self):
       return self.bitStream















# Channel model API
#the functions below simulate a channel, thereby create offsets and shift delays.
class PhaseFrequencyOffset():
  def __init__(self, sample_rate=1, phase_offset=0):
    self.phi = phase_offset
    self.dt = 1/sample_rate
    self.off_phi = 0

  def Offset(self, x, fShift):
    (N,M) = x.shape
    if(type(self.off_phi)==int):
      self.off_phi = np.zeros(M) 
    n = np.arange(0, N)
    arg = np.array([2*np.pi*n*fShift[i]*self.dt + self.off_phi[i] for i in range(0,M)]).T + self.phi
    self.off_phi += 2*np.pi*N*fShift*self.dt
    y = x * (np.cos(arg) + 1j*np.sin(arg))
    return y

  def Release(self):
    self.off_phi = 0

class IntegerDelay():
  def __init__(self, delays):
    self.D_buffer = [np.zeros(i) for i in delays.astype(int)]

  def Delay(self, x):
    y = np.zeros_like(x)
    N = x.shape[0]
    for i in range(0,len(self.D_buffer)):
      [y[:,i], self.D_buffer[i]] = np.split(np.append(self.D_buffer[i], x[:,i]), [N])
    return y


class FractionalDelay():
  def __init__(self, L=4, Dmax=100):
    self.L = L
    self.T = L-1
    if(Dmax > 65535):
      Dmax = 65535
    self.Dmax = Dmax
    self.Dmin = L//2 - 1
    self.H = np.linalg.inv(np.vander(np.arange(0,L), increasing=True).T)
    self.D_buffer = np.empty((0,0))
    self.Nch = -1

  def Delay(self, x, D):
    # If calling first time after empty delay buffer
    if(self.Nch < 0):
      self.Nch = D.shape[0]
      self.D_buffer = np.zeros((self.Dmax+self.T, self.Nch))
    elif(self.Nch != D.shape[0] or self.Nch != x.shape[1]):
      print("Error: Number of channels must remain constant between delay calls")
      return
  
    # Replace indexes with less/greater delay with Dmin/Dmax
    D[D < self.Dmin] = self.Dmin
    D[D > self.Dmax] = self.Dmax
    
    W = (D-self.Dmin).astype(int)
    f = self.Dmin+D-D.astype(int)
    # Columns of h contain filter coeffs
    h = self.H@np.array([f**i for i in range(0, self.L)])
    len = x.shape[0]

    temp = np.append(self.D_buffer, x, axis=0)
    self.D_buffer = temp[-self.D_buffer.shape[0]:]

    beg = self.D_buffer.shape[0]-W-self.T
    jump = len + self.T
    start = self.T
    end = self.T+len
    y = np.array([np.convolve(temp[beg[i]:beg[i]+jump, i], h[:,i])[start:end] for i in range(0,self.Nch)]).T

    return y

  def Release(self):
    self.Nch = -1
    self.D_buffer = np.empty((0,0))
    return

# x - input samples
# SqrtPr - square root of received power
def PowerScale(x, SqrtPr):
    rmsPow = np.sqrt(np.mean(np.abs(x)**2, axis=0))
    rmsPow[rmsPow==0.0] = 1
    scaledsig = SqrtPr*x/rmsPow
    return scaledsig

# Acquisition and Tracking API

def navic_pcps_acquisition(x, prnSeq, fs, fSearch, threshold=0):

    """Performs PCPS (Parallel Code Phase Search using FFT algorithm) acquisition

    :param x: Input signal buffer
    :param prnSeq: Sampled PRN sequence of satellite being searched
    :param fs: Sampling rate
    :param fSearch: Array of Doppler frequencies to search
    :param threshold: Threshold value above which satellite is considered as visible/acquired, defaults to 0
    :return status, codeShift, dopplerShift: status is 'True' or 'False' for signal acquisition. In the case of staus being 'True', it provides coarse estimations of code phase and Doppler shift.
    """

    prnSeqFFT = np.conjugate(np.fft.fft(1-2*prnSeq))
    print(prnSeq.shape)
    
    K = x.shape[0]
    print(K)
    N = fSearch.shape[0]
    print(N)
    ts = 1/fs
    t = np.arange(K)*ts

    Rxd = np.empty((K, N), dtype=np.complex_)
    for i in range(0,N):
        x_iq = x*np.exp(-1j*2*np.pi*fSearch[i]*t)
        XFFT = np.fft.fft(x_iq)
        YFFT = XFFT*prnSeqFFT
        Rxd[:,i] = (1/K)*np.fft.ifft(YFFT)

    maxIndex = np.argmax(np.abs(Rxd)**2)
    maxCol = maxIndex%N
    maxRow = maxIndex//N

    powIn = np.mean(np.abs(x)**2)
    sMax = np.abs(Rxd[maxRow, maxCol])**2
    thresholdEst = 2*K*sMax/powIn

    if(thresholdEst > threshold):
        tau = maxRow
        fDev = fSearch[maxCol]
        return True, tau, fDev
    else:
        return False, 0, 0

#acquisition will provide rough frequency and code offsets. tracking will do precise calculation of frequency shifts and code delays
#thereby locks the values once threshold is reached

class NavicTracker:
    def __init__(self):
        # Public, tunable properties
        self.InitialCodePhaseOffset = 0
        self.InitialDopplerShift = 0
        self.DisablePLL = False
        self.PLLIntegrationTime = 1  # In milliseconds
        self.PLLNoiseBandwidth = 18

        # Signal properties
        self.PRNID = 1
        self.CenterFrequency = 0
        self.SampleRate = 38.192e6  # In Hz

        # Properties of carrier tracking loops
        self.FLLOrder = 1
        self.PLLOrder = 2
        self.FLLNoiseBandwidth = 4

        # Properties of code tracking loop
        self.DLLOrder = 1
        self.DLLNoiseBandwidth = 1

        # Pre-computed constants
        self.ChipRate = 1.023e6  # Chip rate of C/A-code

        # FLL properties
        self.pFLLNaturalFrequency = None
        self.pFLLGain1 = None
        self.pFLLGain2 = None
        self.pFLLGain3 = None
        self.pFLLWPrevious1 = 0
        self.pFLLWPrevious2 = 0
        self.pFLLNCOOut = 0

        # PLL properties
        self.pPLLNaturalFrequency = None
        self.pPLLGain1 = None
        self.pPLLGain2 = None
        self.pPLLGain3 = None
        self.pPLLWPrevious1 = 0
        self.pPLLWPrevious2 = 0
        self.pPLLNCOOut = 0
        self.pPreviousPhase = 0

        # DLL properties
        self.pDLLGain1 = None
        self.pDLLGain2 = None
        self.pDLLGain3 = None
        self.pDLLWPrevious1 = 0
        self.pDLLNCOOut = 0
        self.pDLLNaturalFrequency = None
        self.pPromptCode = None

        # General properties
        self.pNumIntegSamples = None
        self.pSamplesPerChip = None
        self.pReferenceCode = None
        self.pNumSamplesToAppend = 0
        self.pBuffer = None

    def setupImpl(self):

        # Perform one-time calculations, such as computing constants
        self.pNumIntegSamples = self.SampleRate*self.PLLIntegrationTime*1e-3
        # PLLIntegrationTime is in milliseconds. Hence multiply by 1e-3 to get it into sec

        # Calculate loop parameters for DLL
        if self.DLLOrder == 1: # Table 8.23 in Kaplan 3rd edition [1]
            self.pDLLNaturalFrequency = self.DLLNoiseBandwidth/0.25
            self.pDLLGain1 = self.pDLLNaturalFrequency
        elif self.DLLOrder == 2:
            self.pDLLNaturalFrequency = self.DLLNoiseBandwidth/0.53
            self.pDLLGain1 = self.pDLLNaturalFrequency**2
            self.pDLLGain2 = self.pDLLNaturalFrequency*1.414
        else: # self.DLLOrder == 3
            self.pDLLNaturalFrequency = self.DLLNoiseBandwidth/0.7845
            self.pDLLGain1 = self.pDLLNaturalFrequency**3
            self.pDLLGain2 = self.pDLLNaturalFrequency*1.1
            self.pDLLGain3 = self.pDLLNaturalFrequency*2.4

        # Calculate loop parameters for FLL
        if self.FLLOrder == 1: # Table 8.23 in Kaplan 3rd edition [1]
            self.pFLLNaturalFrequency = self.FLLNoiseBandwidth/0.25
            self.pFLLGain1 = self.pFLLNaturalFrequency
        elif self.FLLOrder == 2:
            self.pFLLNaturalFrequency = self.FLLNoiseBandwidth/0.53
            self.pFLLGain1 = self.pFLLNaturalFrequency**2
            self.pFLLGain2 = self.pFLLNaturalFrequency*1.414
        else: # self.FLLOrder == 3
            self.pFLLNaturalFrequency = self.FLLNoiseBandwidth/0.7845
            self.pFLLGain1 = self.pFLLNaturalFrequency**3
            self.pFLLGain2 = self.pFLLNaturalFrequency*1.1
            self.pFLLGain3 = self.pFLLNaturalFrequency*2.4

        # Calculate loop parameters for PLL
        if self.PLLOrder == 1: # Table 8.23 in Kaplan 3rd edition [1]
            self.pPLLNaturalFrequency = self.PLLNoiseBandwidth/0.25
            self.pPLLGain1 = self.pPLLNaturalFrequency
        elif self.PLLOrder == 2:
            self.pPLLNaturalFrequency = self.PLLNoiseBandwidth/0.53
            self.pPLLGain1 = self.pPLLNaturalFrequency**2
            self.pPLLGain2 = self.pPLLNaturalFrequency*1.414
        else: # self.PLLOrder == 3
            self.pPLLNaturalFrequency = self.PLLNoiseBandwidth/0.7845
            self.pPLLGain1 = self.pPLLNaturalFrequency**3
            self.pPLLGain2 = self.pPLLNaturalFrequency*1.1
            self.pPLLGain3 = self.pPLLNaturalFrequency*2.4

        # Initialize the code
        numCACodeBlocks = self.PLLIntegrationTime # Each C/A-code block is of 1 milliseconds.
        code = 1 - 2 * genNavicCaCode(self.PRNID).astype(float)
        self.pSamplesPerChip = self.SampleRate / self.ChipRate
        sampleFactor = Fraction(self.pSamplesPerChip)
        upSampleFactor = sampleFactor.numerator; downSampleFactor = sampleFactor.denominator
        numSamplesPerCodeBlock = self.SampleRate * 1e-3 # As each code block is of 1e-3 seconds
        upwave1 = np.repeat(code, upSampleFactor)
        self.pPromptCode = np.tile(upwave1[::downSampleFactor], numCACodeBlocks)

        # Calculate number of samples in delay
        numsamprot = round(self.InitialCodePhaseOffset * self.pSamplesPerChip) # Number of samples to rotate
        self.pNumSamplesToAppend = numSamplesPerCodeBlock - (numsamprot % numSamplesPerCodeBlock)

    def stepImpl(self, u):
        # Implement algorithm. Calculate y as a function of input u and
        # discrete states.
        
        coarsedelay = round(self.pNumSamplesToAppend)    # Me added round()
        numSamplesPerCodeBlock = self.SampleRate * 1e-3  # As each code block is of 1e-3 seconds
        finedelay = round(self.pDLLNCOOut * self.pSamplesPerChip)
        
        if len(self.pBuffer) != coarsedelay + finedelay:
            numextradelay = coarsedelay + finedelay - len(self.pBuffer)
            if numextradelay > 0:
                self.pBuffer = np.concatenate([np.zeros(numextradelay), self.pBuffer])
            else:  # numextradelay < 0. Equal to zero is not possible because of the first if condition
                if abs(numextradelay) < len(self.pBuffer):
                    # Remove samples from pBuffer itself
                    self.pBuffer = self.pBuffer[abs(numextradelay):]
                else:
                    n = numSamplesPerCodeBlock + numextradelay
                    self.pBuffer = np.concatenate([np.zeros(n), self.pBuffer])
        

        # Buffer the input
        integtime = self.PLLIntegrationTime*1e-3 # PLLIntegrationTime is in milliseconds. Hence multiply by 1e-3 to get it into sec
        [u, self.pBuffer] = np.split(np.append(self.pBuffer, u), [round(self.SampleRate*integtime)])

        # Carrier wipe-off
        fc = self.CenterFrequency + self.InitialDopplerShift - self.pFLLNCOOut
        t = np.arange(self.pNumIntegSamples+1)/self.SampleRate
        phases = 2*np.pi*fc*t + self.pPreviousPhase - self.pPLLNCOOut
        iqsig = u * np.exp(-1j*phases[:-1])
        self.pPreviousPhase = phases[-1] + self.pPLLNCOOut

        # Code wipe-off
        # Update the prompt code appropriately

        numSamplesPerHalfChip = round(self.pSamplesPerChip/2)
        iq_e = iqsig * np.roll(self.pPromptCode, -1*numSamplesPerHalfChip)
        iq_p = iqsig * self.pPromptCode
        iq_l = iqsig * np.roll(self.pPromptCode, numSamplesPerHalfChip)
        integeval = np.sum(iq_e)
        integlval = np.sum(iq_l)

        millisecdata = iq_p.reshape((self.PLLIntegrationTime, -1)).T # Each column contains one millisecond of data
        y = np.sum(millisecdata, axis=0) # Each element contains integrated value of one millisecond of data
        integpval = np.sum(y)
        if len(iq_p) % 2 != 0: # Odd number of samples
            fllin = np.sum(np.reshape(np.concatenate([iq_p, [0]]), (2, -1)).T, axis=0) # Append a zero
        else:
            fllin = np.sum(iq_p.reshape((2, -1)).T, axis=0)

        # DLL discriminator
        E = np.abs(integeval)
        L = np.abs(integlval)
        delayerr = (E-L)/(2*(E+L)) # Non-coherent early minus late normalized detector

        # DLL loop filter
        if self.DLLOrder == 2:
            # 1st integrator
            wcurrent = delayerr*self.pDLLGain1*integtime + self.pDLLWPrevious1
            loopfilterout = (wcurrent + self.pDLLWPrevious1)/2 + delayerr*self.pDLLGain2
            self.pDLLWPrevious1 = wcurrent  # Acceleration accumulator
        elif self.DLLOrder == 1:
            loopfilterout = delayerr*self.pDLLGain1

        # DLL NCO
        delaynco = self.pDLLNCOOut + integtime*loopfilterout
        self.pDLLNCOOut = delaynco

        # FLL discriminator
        phasor = np.conj(fllin[0])*fllin[1]
        # phasor = np.conj(self.pPreviousIntegPVal)*integpval
        fqyerr = -1*np.angle(phasor)/(np.pi*integtime)  # Multiplication by 2 is removed because integtime of FLL is half of that of PLL

        # FLL loop filter
        if self.FLLOrder == 2:
            # 1st integrator
            wcurrent = fqyerr*self.pFLLGain1*integtime + self.pFLLWPrevious1
            loopfilterout = (wcurrent + self.pFLLWPrevious1)/2 + fqyerr*self.pFLLGain2
            self.pFLLWPrevious1 = wcurrent # Acceleration accumulator
        elif self.FLLOrder == 1:
            loopfilterout = fqyerr*self.pFLLGain1

        # FLL NCO
        fqynco = self.pFLLNCOOut + integtime*loopfilterout
        self.pFLLNCOOut = fqynco

        # PLL discriminator
        if self.DisablePLL:
            pherr = 0
        else:
            pherr = np.arctan(np.real(integpval)/np.imag(integpval))
        
        # PLL loop filter
        if self.PLLOrder == 3:
            # 1st integrator
            wcurrent = pherr*self.pPLLGain1*integtime + self.pPLLWPrevious1
            integ1out = (wcurrent + self.pPLLWPrevious1)/2 + pherr*self.pPLLGain2
            self.pPLLWPrevious1 = wcurrent # Acceleration accumulator

            # 2nd integrator
            wcurrent = integ1out*integtime + self.pPLLWPrevious2
            loopfilterout = (wcurrent + self.pPLLWPrevious2)/2 + pherr*self.pPLLGain3
            self.pPLLWPrevious2 = wcurrent # Velocity accumulator
        elif self.PLLOrder == 2:
            wcurrent = pherr*self.pPLLGain1*integtime + self.pPLLWPrevious1
            loopfilterout = (wcurrent + self.pPLLWPrevious1)/2 + pherr*self.pPLLGain2
            self.pPLLWPrevious1 = wcurrent # Velocity accumulator

        # PLL NCO
        phnco = self.pPLLNCOOut + integtime*loopfilterout
        self.pPLLNCOOut = phnco

        return y, fqyerr, fqynco, pherr, phnco, delayerr, delaynco

    def resetImpl(self):
        # Initialize / reset discrete-state properties
        self.pBuffer = np.zeros(round(self.pNumSamplesToAppend))
        self.pFLLWPrevious1 = 0
        self.pFLLWPrevious2 = 0
        self.pFLLNCOOut = 0
        self.pPLLWPrevious1 = 0
        self.pPLLWPrevious2 = 0
        self.pPLLNCOOut = 0
        self.pDLLWPrevious1 = 0
        self.pDLLNCOOut = 0
#end of acquisition and tracking code
