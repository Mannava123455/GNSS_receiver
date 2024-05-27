import numpy as np
c = np.fromfile("/home/mannava/gps_sdr/gps-sdr-sim/gpssim.bin",np.int8)

dataI = c[0::2]
dataQ = c[1::2]

data = dataI + 1j*dataQ
SNR_dB = -22
power = 10**(-SNR_dB/10)
noise = (np.random.normal(scale=power**0.5, size=(20480, )) + 1j*np.random.normal(scale=power**0.5, size=(20480, )))/2**0.5
#noise_signal = data + noise
noise_signal = data
sig = noise_signal[0:20480]
fc = 15000
t = np.arange(20480)/2048000
phases = 2*np.pi*fc*t 
iqsig = sig * np.exp(-1j*phases)
s = iqsig #+ noise
i = np.real(s)
q = np.imag(s)


np.savetxt("i.dat",i)
np.savetxt("q.dat",q)


p =  data[0:20480]

b_i = np.real(p)
b_q = np.imag(p)


np.savetxt("b_i.dat",b_i)
np.savetxt("b_q.dat",b_q)
