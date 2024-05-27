import numpy as np
import matplotlib.pyplot as plt

p=np.loadtxt("carrErr.dat")
f = np.loadtxt("freqErr.dat")
d = np.loadtxt("delayerr.dat")



plt.subplot(3,1,1)
plt.plot(p[0:])
plt.xlabel("time")
plt.ylabel("phaseerr")


plt.subplot(3,1,2)
plt.plot(f[0:])
plt.xlabel("time")
plt.ylabel("freqerr")

plt.subplot(3,1,3)
plt.plot(d[0:])
plt.xlabel("time")
plt.ylabel("delayerr")

plt.show()
