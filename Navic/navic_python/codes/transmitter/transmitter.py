import numpy as np

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

#function to generate the PRN sequrnce given the satellite ID
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
def genNavicCaTable(samplingFreq):
    prnIdMax = 14
    codeLength = 1023
    codeFreqBasis = 1.023e6
    samplingPeriod = 1/samplingFreq
    sampleCount = int(np.round(samplingFreq / (codeFreqBasis / codeLength)))
    indexArr = (np.arange(sampleCount)*samplingPeriod*codeFreqBasis).astype(np.float32)     # Avoid floating point error due to high precision
    indexArr = indexArr.astype(int)
    return np.array([genNavicCaCode(i) for i in range(1,prnIdMax+1)])[:,indexArr].T
    
    

#class to generate navigation data at 50sps  (random bits)
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
    


# Bit generation and Modulation API
#class below will generate modulated IQ samples, follows ICD
class NavicL5sModulator():
    def __init__(self, fs):
        self.sampleRate = fs
        self.codePhase = 0

        # BOC(m,n) Init
        self.m = 5; self.n = 2
        fsc = self.m*1.023e6
        epsilon = fsc*1/(100*self.sampleRate)
        self.subCarrPhase = epsilon 

    # columns of x have samples
    # columns of codeTable have sampled PRN sequence
    def Modulate(self, x, codeTable):

        codeNumSample = codeTable.shape[0]
        numSample = x.shape[0]
        numChannel = x.shape[1]

        spsBpskSig = 1-2*np.logical_xor(x, codeTable[np.arange(self.codePhase, self.codePhase+numSample)%codeNumSample, :])

        # Subcarrier generation for BOC
        subCarr1Ch = self.__GenBocSubCarrier(numSample)
        SubCarrSig = np.tile(np.array([subCarr1Ch]).T, (1, numChannel))

        # PRN sequence of SPS is RS pilot PRN sequence
        PilotCode = np.tile(codeTable[np.arange(self.codePhase, self.codePhase+numSample)%codeNumSample, :], (self.n, 1))[0::self.n]
        PilotSig = 1-2*PilotCode
        # Data for RS is data of SPS
        DataSig = 1-2*x

        rsBocPilotSig = PilotSig * SubCarrSig
        rsBocDataSig = DataSig * SubCarrSig

        interplexSig = spsBpskSig * rsBocDataSig * rsBocPilotSig

        self.codePhase = (self.codePhase+numSample)%codeNumSample

        alpha = (2**0.5)/3
        beta = 2/3
        gamma = 1/3
        iqsig = alpha*(spsBpskSig + rsBocPilotSig) + 1j*(beta*rsBocDataSig - gamma*interplexSig)  # Document formula

        return iqsig
    
    def __GenBocSubCarrier(self, N):
       ts = 1/self.sampleRate
       t = np.arange(N)*ts
       
       fsc = self.m*1.023e6
       subCarrier = np.sign(np.sin(2*np.pi*(fsc*t + self.subCarrPhase))) 
       self.subCarrPhase += fsc*N*ts
       self.subCarrPhase -= int(self.subCarrPhase)
       return subCarrier

    def Release(self):
        self.codePhase = 0

        fsc = self.m*1.023e6
        epsilon = fsc*1/(100*self.sampleRate)
        self.subCarrPhase = epsilon


