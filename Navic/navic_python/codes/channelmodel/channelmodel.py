import numpy as np

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
    rmsPow = np.real(np.sqrt(np.mean(np.abs(x)**2, axis=0)))
    rmsPow[rmsPow==0.0] = 1
    scaledsig = SqrtPr*x/rmsPow
    return scaledsig

# Testing code
if __name__ == "__main__":

    writedir = "/home/mh/navic/chtest/"

    statdel_file = "staticdelay"
    fshift_file = "fshift"
    vardel_file = "variabledelay"
    sqrtpr_file = "sqrtpr"
    input_file = "input"
    output_file = "output"
    dopp_file = "doppler"
    intdel_file = "intdel"
    fracdel_file = "fracdel"

    ext = ".txt"

    # Initializations
    sampleRate = 10.23e6
    pfo = PhaseFrequencyOffset(sampleRate)

    statD = np.loadtxt(writedir+statdel_file+ext,delimiter=',')
    intd = IntegerDelay(statD)

    fracd = FractionalDelay(4, 65535)

    error = 0

    for i in range(1,1500+1):

      ts = str(i)

      iqsig = np.loadtxt(writedir+input_file+ts+ext, delimiter=',', dtype=np.complex128)
      compsig = np.loadtxt(writedir+output_file+ts+ext, delimiter=',', dtype=np.complex128)

      fShift = np.loadtxt(writedir+fshift_file+ts+ext, delimiter=',')
      varD = np.loadtxt(writedir+vardel_file+ts+ext, delimiter=',')
      powersig = np.loadtxt(writedir+sqrtpr_file+ts+ext, delimiter=',')

      doppSig = pfo.Offset(iqsig, fShift)

      statdSig = intd.Delay(doppSig)

      dyndSig = fracd.Delay(statdSig, varD)

      scaledSig = PowerScale(dyndSig, powersig)

      outsig = scaledSig

      error += np.sum(np.abs(outsig-compsig))

      print(ts)


    print("Final Error: ", error)
