import numpy as np
from fractions import Fraction
from sk_dsp_comm import fec_conv as fec     #pip/pip3 install scikit-dsp-comm
import sk_dsp_comm.digitalcom as dc

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

def genNavicCaTable(samplingFreq):
    """Upsample the CA code(PRN) to the given sampling frequency
    
    :param int samplingFreq: frequency to upsample to
    :returns list: upsampled CA code 
        
    """
    prnIdMax = 14 
    codeLength = 1023 
    codeFreqBasis = 1.023e6
    samplingPeriod = 1/samplingFreq
    sampleCount = int(np.round(samplingFreq / (codeFreqBasis / codeLength)))
    indexArr = (np.arange(sampleCount)*samplingPeriod*codeFreqBasis).astype(np.float32)     # Avoid floating point error due to high precision
    indexArr = indexArr.astype(int)
    return np.array([genNavicCaCode(i) for i in range(1,prnIdMax+1)])[:,indexArr].T     # column-wise PRN Sequence for all 14 satellites

#function to compute crc-24q parity
def rtk_crc24q(buff, length):
    """Build the CRC Code

    buff (contains the subframe bits right aligned i.e. additional zeros padded in first byte)\n
    For ex: If the bits are 1101010001111001010100100111 (28 bits), they are stored in buff as\n
    00001101 | 01000111 | 10010101 | 00100111\n
    b0   |    b1    |    b2    |    b3
    
    :param list buff: navdata
    :param int length: length of navdata
    :returns list crc: crc-24Q parity
    
    """    
    if length%8!=0:
        zero = 8-(length%8)
        buff = np.concatenate((np.zeros(zero,dtype=np.uint8),buff))
        length+=zero
    
    packed_data = np.packbits(buff.reshape(-1,8))
    crc = 0
    
    
    for i in range(int(length/8)):
        crc = ((crc << 8) & 0xFFFFFF) ^ tbl_CRC24Q[(crc >> 16) ^ packed_data[i]]

    return crc

tbl_CRC24Q = [
    0x000000,0x864CFB,0x8AD50D,0x0C99F6,0x93E6E1,0x15AA1A,0x1933EC,0x9F7F17,
    0xA18139,0x27CDC2,0x2B5434,0xAD18CF,0x3267D8,0xB42B23,0xB8B2D5,0x3EFE2E,
    0xC54E89,0x430272,0x4F9B84,0xC9D77F,0x56A868,0xD0E493,0xDC7D65,0x5A319E,
    0x64CFB0,0xE2834B,0xEE1ABD,0x685646,0xF72951,0x7165AA,0x7DFC5C,0xFBB0A7,
    0x0CD1E9,0x8A9D12,0x8604E4,0x00481F,0x9F3708,0x197BF3,0x15E205,0x93AEFE,
    0xAD50D0,0x2B1C2B,0x2785DD,0xA1C926,0x3EB631,0xB8FACA,0xB4633C,0x322FC7,
    0xC99F60,0x4FD39B,0x434A6D,0xC50696,0x5A7981,0xDC357A,0xD0AC8C,0x56E077,
    0x681E59,0xEE52A2,0xE2CB54,0x6487AF,0xFBF8B8,0x7DB443,0x712DB5,0xF7614E,
    0x19A3D2,0x9FEF29,0x9376DF,0x153A24,0x8A4533,0x0C09C8,0x00903E,0x86DCC5,
    0xB822EB,0x3E6E10,0x32F7E6,0xB4BB1D,0x2BC40A,0xAD88F1,0xA11107,0x275DFC,
    0xDCED5B,0x5AA1A0,0x563856,0xD074AD,0x4F0BBA,0xC94741,0xC5DEB7,0x43924C,
    0x7D6C62,0xFB2099,0xF7B96F,0x71F594,0xEE8A83,0x68C678,0x645F8E,0xE21375,
    0x15723B,0x933EC0,0x9FA736,0x19EBCD,0x8694DA,0x00D821,0x0C41D7,0x8A0D2C,
    0xB4F302,0x32BFF9,0x3E260F,0xB86AF4,0x2715E3,0xA15918,0xADC0EE,0x2B8C15,
    0xD03CB2,0x567049,0x5AE9BF,0xDCA544,0x43DA53,0xC596A8,0xC90F5E,0x4F43A5,
    0x71BD8B,0xF7F170,0xFB6886,0x7D247D,0xE25B6A,0x641791,0x688E67,0xEEC29C,
    0x3347A4,0xB50B5F,0xB992A9,0x3FDE52,0xA0A145,0x26EDBE,0x2A7448,0xAC38B3,
    0x92C69D,0x148A66,0x181390,0x9E5F6B,0x01207C,0x876C87,0x8BF571,0x0DB98A,
    0xF6092D,0x7045D6,0x7CDC20,0xFA90DB,0x65EFCC,0xE3A337,0xEF3AC1,0x69763A,
    0x578814,0xD1C4EF,0xDD5D19,0x5B11E2,0xC46EF5,0x42220E,0x4EBBF8,0xC8F703,
    0x3F964D,0xB9DAB6,0xB54340,0x330FBB,0xAC70AC,0x2A3C57,0x26A5A1,0xA0E95A,
    0x9E1774,0x185B8F,0x14C279,0x928E82,0x0DF195,0x8BBD6E,0x872498,0x016863,
    0xFAD8C4,0x7C943F,0x700DC9,0xF64132,0x693E25,0xEF72DE,0xE3EB28,0x65A7D3,
    0x5B59FD,0xDD1506,0xD18CF0,0x57C00B,0xC8BF1C,0x4EF3E7,0x426A11,0xC426EA,
    0x2AE476,0xACA88D,0xA0317B,0x267D80,0xB90297,0x3F4E6C,0x33D79A,0xB59B61,
    0x8B654F,0x0D29B4,0x01B042,0x87FCB9,0x1883AE,0x9ECF55,0x9256A3,0x141A58,
    0xEFAAFF,0x69E604,0x657FF2,0xE33309,0x7C4C1E,0xFA00E5,0xF69913,0x70D5E8,
    0x4E2BC6,0xC8673D,0xC4FECB,0x42B230,0xDDCD27,0x5B81DC,0x57182A,0xD154D1,
    0x26359F,0xA07964,0xACE092,0x2AAC69,0xB5D37E,0x339F85,0x3F0673,0xB94A88,
    0x87B4A6,0x01F85D,0x0D61AB,0x8B2D50,0x145247,0x921EBC,0x9E874A,0x18CBB1,
    0xE37B16,0x6537ED,0x69AE1B,0xEFE2E0,0x709DF7,0xF6D10C,0xFA48FA,0x7C0401,
    0x42FA2F,0xC4B6D4,0xC82F22,0x4E63D9,0xD11CCE,0x575035,0x5BC9C3,0xDD8538 ]


class NavicL5sModulator():
    """NavicL5sModulator will generate modulated IQ samples
    
    """

    def __init__(self, fs):
        """The init function is executed always when class is initiated
        
        :param float fs: sample rate
        
        """
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
        """Modulate the samples and PRN sequence according to ICD
        
        :param list x: nav data samples
        :param list codeTable: upsampled CA code table
        :returns list iqsig: baseband modulated signal

        """
        codeNumSample = codeTable.shape[0]
        numSample = x.shape[0]
        numChannel = x.shape[1]

        spsBpskSig = 1-2*np.logical_xor(x, codeTable[np.arange(self.codePhase, self.codePhase+numSample)%codeNumSample, :])     # BPSK Modulated (SPS XOR PRN)

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
       """Function to generate Binary Offset sub carrier signal

       :param int N: Number of samples to generate
       :returns subCarrier: Boc signal

       """
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

#class to generate navigation data at 50sps
class NavicDataGen():
    """NavicDataGen generates raw samples of data
    
    """
    
    def __init__(self, ds=50, fs=10*1.023e6, numChannel=1, file=None):
        """The init function is executed always when class is initiated

        :param int ds: data rate/bit rate
        :param int fs: sample rate
        :param int numChannel: number of Channels
        :param bool file: data file if present

        """
        self.dataRate = ds
        self.sampleRate = fs
        self.numSymbolsPerFrame = 2400
        self.numSymbolsPerSubFrame = 600
        self.numDataBitsPerSubFrame = 292
        self.numSamplesPerBit = round(fs/ds)
        self.samplesToNextBit = self.numSamplesPerBit
        self.numChannel = numChannel
        self.bitcnt = 0

        self.bitStream = np.empty((0, numChannel))
        self.datStream = np.empty((0, numChannel))
        full_frame = np.empty(0)
        full_data = np.empty(0)
        for i in range(numChannel):
            frame, data = self.__frameGen()
            full_frame = np.append(full_frame,frame)
            full_data = np.append(full_data,data)

        self.bitStream = np.append(self.bitStream,full_frame.reshape(numChannel,-1).T,axis=0)
        self.datStream = np.append(self.datStream,full_data.reshape(numChannel,-1).T,axis=0)


    def GenerateBits(self, timeInterval):
      """Function to generate bits upto given time interval
      
      :param float timeInterval: time interval required
      :returns list genStream: bits upto given time interval
      
      """
      genStream = np.empty((1,self.numChannel))
      numBitsToGen = round(self.sampleRate*timeInterval)

      bufferCnt = numBitsToGen 
      # Main loop to generate sampled bits for given time interval
      while bufferCnt > 0: 
        # If remaining samples to generate is within the current bit's remaining duration
        if(bufferCnt < self.samplesToNextBit):
          # Copy current bit
          genStream = np.append(genStream, np.repeat(self.bitStream[self.bitcnt: self.bitcnt+1,:], bufferCnt, axis=0), axis=0)
          # Update current bit's remaining duration
          self.samplesToNextBit -= bufferCnt
          # End loop
          bufferCnt = -1
        else:
          # Copy current bit for remaining duration
          genStream = np.append(genStream, np.repeat(self.bitStream[self.bitcnt: self.bitcnt+1,:], self.samplesToNextBit, axis=0), axis=0)
          # Increment bit counter
          self.bitcnt+=1
          # If current frame ended, generate new frame
          if(self.bitcnt%self.numSymbolsPerFrame==0):
            full_frame = np.empty(0)
            full_data = np.empty(0)
            for i in range(self.numChannel):
                frame, data = self.__frameGen()
                full_frame = np.append(full_frame,frame)
                full_data = np.append(full_data,data)

            self.bitStream = np.append(self.bitStream,full_frame.reshape(self.numChannel,-1).T,axis=0)
            self.datStream = np.append(self.datStream,full_data.reshape(self.numChannel,-1).T,axis=0)
          # Update remaining samples to generate
          bufferCnt -= self.samplesToNextBit
          # Update remaining duration of current bit
          self.samplesToNextBit = self.numSamplesPerBit
      
      return genStream[1:numBitsToGen+1]
    
    def __frameGen(self):
        """Function to add CRC, tail bits, interleave and encode the data bits

        :returns list frame: encoded symbols 
        :returns list nav_data: pre-encoded data

        """
        nav_data = np.array([])
        frame = np.array([],dtype=int)
        for i in range(4): 
            data = np.array([np.random.randint(0, 2) for _ in range(262)])
            cr = rtk_crc24q(data, len(data))
            crc = "{:06X}".format(cr)
            binary = bin(int(crc,16))[2:]
            padded_binary = list(binary.zfill(len(crc) * 4))
            nav_crc = np.append(data,padded_binary)
            nav_crc = np.array([int(bit) for bit in nav_crc])

        #fec encoding and tail bits
            nav_crc_tail = np.append(nav_crc,np.zeros(6)) #tail bits
            nav_data = np.append(nav_data,nav_crc_tail)
            state = '000000'
            cc1 = fec.FECConv(('1111001','1011011'))
            nav_encd,state = cc1.conv_encoder(nav_crc_tail,state)

        #interleaving
            k=8
            n= 73
            interleave = lambda x,k,n: x.reshape(n,-1).T.flatten()
            nav_intrlv = interleave(nav_encd,k,n)

        #adding sync word EB90 Hex
            sync_hex = 'EB90'
            sync_bin = bin(int(sync_hex,16))[2:]
            sync_bin = [int(bit) for bit in sync_bin]
            encsubframe = np.append(sync_bin,nav_intrlv)
            frame = np.append(frame,encsubframe)

        return frame, nav_data


    def GetBitStream(self):
       """Function to return bitstream of nav data
             
       :returns list genStream: generated bits

       """
       numBitsGen = (self.bitcnt//self.numSymbolsPerSubFrame)*self.numDataBitsPerSubFrame
       remain = self.bitcnt%self.numSymbolsPerSubFrame
       if(remain>=16):
          numBitsGen += (remain-16)//2
       return self.datStream[0:numBitsGen]
      
# Channel model API
#the functions below simulate a channel, thereby create offsets and shift delays.
class PhaseFrequencyOffset():
  """Class to generate phase and frequency offset for channel simualtion
  
  """
  def __init__(self, sample_rate=1, phase_offset=0):
    """The init function is executed always when class is initiated
    :param int sample_rate: 1
    :param int phase_offset: 0
    
    """
    self.phi = phase_offset
    self.dt = 1/sample_rate
    self.off_phi = 0

  def Offset(self, x, fShift):
    """Applies Doppler shift to incoming signal
    
    :param list x: nav data signal
    :param list fShift: list of frequency shifts applied to signal

    """
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
  """Delay the incoming signal by integer number of samples

  """
  def __init__(self, delays):
    """The init function is executed always when class is initiated
    
    :param int delays: delay value to be applied
    
    """
    self.D_buffer = [np.zeros(i) for i in delays.astype(int)]

  def Delay(self, x):
    """function to delay the input signal
    
    :param list x: input signal
    :returns list y: delayed input signal
    
    """
    y = np.zeros_like(x)
    N = x.shape[0]
    for i in range(0,len(self.D_buffer)):
      [y[:,i], self.D_buffer[i]] = np.split(np.append(self.D_buffer[i], x[:,i]), [N])
    return y


class FractionalDelay():
  """Delay the incoming signal by fractional number of samples
  
  """
  def __init__(self, L=4, Dmax=100):
    """The init function is executed always when class is initiated
    
    :param int L: Filter length
    :param int Dmax: maximum delay value
    
    """
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
    """Delays the incoming signal by given fractional delay value
    
    :param list x: incoming signal
    :param list D: fractional delay values for multiple channels
    :returns list y: delayed incoming signal"""

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
    """Scale the incoming signal's power by given factor
    
    :param list x: incoming signal
    :param list SqrtPr: list of factors
    :returns list scaledsig: scaled incoming signal by given factor"""
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
    
    K = x.shape[0]
    N = fSearch.shape[0]
    ts = 1/fs
    t = np.arange(K)*ts

    Rxd = np.empty((K, N), dtype=np.complex_)

    for i in range(0,N):       #  Multiplication of IQ waveform and conjugate PRN sequence in frequency domain per frequency step
        x_iq = x*np.exp(-1j*2*np.pi*fSearch[i]*t)
        XFFT = np.fft.fft(x_iq)
        YFFT = XFFT*prnSeqFFT
        Rxd[:,i] = (1/K)*np.fft.ifft(YFFT)      # IFFT for final product

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
    """NavicTracker will implement the carrier and code tracking loops
    
    """
    def __init__(self):
        """The init function is executed always when class is initiated

        """
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
        """ This will initialize all the tracking loop parameters

        """

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
        numSamplesPerCodeBlock = self.SampleRate * 1e-3 # As each code block is of 1e-3 seconds
        self.pPromptCode = np.tile(self.__upsample_table(code, self.SampleRate), numCACodeBlocks)

        # Calculate number of samples in delay
        numsamprot = round(self.InitialCodePhaseOffset * self.pSamplesPerChip) # Number of samples to rotate
        self.pNumSamplesToAppend = numSamplesPerCodeBlock - (numsamprot % numSamplesPerCodeBlock)

    def stepImpl(self, u):
        """This will execute the tracking loops for fixed integration time

        """
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
    
    def __upsample_table(self, codeBase, samplingFreq):
        """Upsample PRN sequence of satellite being tracked
     
        :param list codeBase: PRN sequence for complete period
        :param list samplingFreq: Desired sampling frequency
        :returns list y: Sampled PRN sequence"""
        codeLength = 1023
        codeFreqBasis = 1.023e6
        samplingPeriod = 1/samplingFreq
        sampleCount = int(np.round(samplingFreq / (codeFreqBasis / codeLength)))
        indexArr = (np.arange(sampleCount)*samplingPeriod*codeFreqBasis).astype(np.float32)     # Avoid floating point error due to high precision
        indexArr = indexArr.astype(int)
        return codeBase[indexArr]

    def resetImpl(self):
        """This will reset the tracking loops
        
        """
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

#function for bit synchronization index
def gnss_bit_synchronize(data, n):
    """Bit synchronization for IRNSS receiver
    
    :param list data: samples from tracking loop
    :param int n: samples per bit
    :returns int syncidx: returns the bit starting index
    
    """
    # Input validation
    numdata = len(data)
    if not isinstance(data, (np.ndarray, list)):
        raise ValueError("Invalid input type for 'data'. Expected ndarray or list.")
    if not isinstance(n, (int, np.integer)) or n <= 0:
        raise ValueError("Invalid input type or value for 'n'. Expected positive integer.")
    if numdata < n:
        raise ValueError("Invalid input length. 'data' should have length greater than or equal to 'n'.")

    # Find the transition locations in the data by finding the difference of signs in adjacent data
    all_signs = np.concatenate(([1], np.sign(data)))
    diff_vals = np.diff(all_signs)
    transition_flags = diff_vals != 0

    # Find the number of transitions at each data location
    ntemp = np.uint16(n)
    num_avg_samples = np.uint64(np.floor(numdata/ntemp) * ntemp)
    trmat = np.reshape(transition_flags[:num_avg_samples], (-1, ntemp)).T

    # Consolidate the number of transitions at each sample location
    numtr = np.sum(trmat, axis=1)

    # Find the starting location corresponding to maximum transitions and cast the value
    syncidx = np.argmax(numtr, axis=0)
    syncidx = np.uint16(syncidx)

    return syncidx

#function for frame synchronization index
SYNC_WORD = [1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0]  # Sync word value
INV_SYNC_WORD = [0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1] # Inverted Sync word value (to check in case of inverted bits)
def find_sync_word(data):
    """Frame synchronization for IRNSS receiver
    
    :param list data: samples from tracking loop
    :returns int status: indicator for presence of sync word
    :returns int fsync_index: returns the frame starting index
    
    """
    sync_word_length = len(SYNC_WORD)
    window = []
    fsync_index = -1
    status = 0

    for index, bit in enumerate(data):
        window.append(bit)
        if len(window) > sync_word_length:
            window.pop(0)
        if window == SYNC_WORD:
            status = 1
            fsync_index = index - sync_word_length + 1
        elif window == INV_SYNC_WORD:
            status = -1
            fsync_index = index - sync_word_length + 1

    return status, fsync_index

def decoder(subframe, num_sf):
    """Function decodes the subframes
    :param list subframe: subframes from the extracted frame after frame synchronization
    :param int num_sf: number of suframes found
    :return list decd_total: returns decoded nav_data

    """
    decd_total = np.empty(0)
    cc1 = fec.FECConv(('1111001','1011011'))
    #remove sync word
    for buff in subframe:
        rec_subframe = buff[16:]

        k = 8
        n = 73

    #undo interleaving
        deinterleave = lambda x,k,n: x.reshape(k,-1).T.flatten()
        nav_deintrv = deinterleave(rec_subframe,k,n)
        nav_deintrv = [int(bit) for bit in nav_deintrv]
        nav_deintrv = np.asarray(nav_deintrv)
        nav_deintrv = np.append(nav_deintrv,np.zeros(6)) #to nullify error in viterbi decoder


    #fec decoding and ber
        yn_hard = ((np.sign(nav_deintrv.real)+1)/2).astype(int)
        nav_decd = cc1.viterbi_decoder(yn_hard,'hard')
        decd_total = np.append(decd_total,nav_decd) 

    return decd_total