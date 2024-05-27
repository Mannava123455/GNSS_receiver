import numpy as np
import math

iq_samples = np.fromfile("gpssim.bin",np.int8)
data_i = iq_samples[0::2]
data_q = iq_samples[1::2]

data = data_i + 1j*data_q

SNR_dB = -22
power = 10**(SNR_dB/10)
noise = (np.random.normal(scale=power**0.5, size=(len(data_i), )) + 1j*np.random.normal(scale=power**0.5, size=(len(data_i), )))/2**0.5
noise_signal = data + noise




