import numpy as np

data = np.loadtxt("freqnco.dat")
mi = min(data)
ma = max(data)
m = np.mean(data)
v = np.var(data)
print(m)
print(mi)
print(ma)
print(v)
