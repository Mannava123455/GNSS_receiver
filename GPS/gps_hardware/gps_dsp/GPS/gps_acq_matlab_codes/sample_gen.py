import numpy as np
c = np.fromfile("gpssim.bin",np.int8)

dataI = c[0::2]
dataQ = c[1::2]

data = dataI + 1j*dataQ


#baseband samples
p =  data[0:4096]
b_i = np.real(p)
b_q = np.imag(p)
np.savetxt("baseband_i_without_drift_and_noise.dat",b_i)
np.savetxt("baseband_q_without_drift_and_noise.dat",b_q)




sig = data[0:4096]
fc = 15000
t = np.arange(4096)/2048000
phases = 2*np.pi*fc*t 
iqsig = sig * np.exp(-1j*phases)

shifted_signal = iqsig 
i = np.real(shifted_signal)
q = np.imag(shifted_signal)

I = []
Q = []

for k in range(0,len(i)):
    I.append(int(i[k]))

for l in range(0,len(i)):
    Q.append(int(q[l]))



np.savetxt("i_with_15khz_drift_without_noise.dat",I)
np.savetxt("q_with_15khz_drift_without_noise.dat",Q)




#samples with noise and 15khz drift

SNR_dB = -22
power = 10**(-SNR_dB/10)
noise = (np.random.normal(scale=power**0.5, size=(4096, )) + 1j*np.random.normal(scale=power**0.5, size=(4096, )))/2**0.5
iqsig = sig * np.exp(-1j*phases)
shifted_signal_with_noise = iqsig + noise
i_n = np.real(shifted_signal)
q_n = np.imag(shifted_signal)

I_n = []
Q_n = []

for k in range(0,len(i_n)):
    I_n.append(int(i_n[k]))

for l in range(0,len(i_n)):
    Q_n.append(int(q_n[l]))

np.savetxt("i_with_15khz_drift_with_noise.dat",I_n)
np.savetxt("q_with_15khz_drift_with_noise.dat",Q_n)
