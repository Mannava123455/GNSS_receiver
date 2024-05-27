import numpy as np
import matplotlib.pyplot as plt



f_n = np.loadtxt("freqnco.dat")
f_e = np.loadtxt("freq_err.dat")
p_n = np.loadtxt("phase_nco.dat")
p_e = np.loadtxt("phase_err.dat")
d_e = np.loadtxt("delay_err.dat")
d_n = np.loadtxt("delay_nco.dat")


plt.subplot(6,1,1)
plt.plot(f_n)
plt.ylabel("freq_nco")

plt.subplot(6,1,2)
plt.plot(f_e)
plt.ylabel("freq_err")

plt.subplot(6,1,3)
plt.plot(p_n)
plt.ylabel("phase_nco")

plt.subplot(6,1,4)
plt.plot(p_e)
plt.ylabel("phase_err")



plt.subplot(6,1,5)
plt.plot(d_n)
plt.ylabel("delay_nco")

plt.subplot(6,1,6)
plt.plot(d_e)
plt.ylabel("delay_err")

plt.show()
