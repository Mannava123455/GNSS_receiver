import numpy as np
import math


iode=47
c_rs=-77.40625
delta_n=4.806985944545E-09
M_0=0.5313197114844
c_uc=-4.196539521217E-06
e=0.01570839330088
c_us=3.710389137268E-06
A=5153.635400772*5153.635400772
t_oe=388800
c_ic=-1.862645149231E-07
omega_0=-1.768535477436
c_is=-2.048909664154E-08
i_0=0.9574058050976
c_rc=307.59375
omega=1.45578683932
omega_dot=-8.739292598044E-09
idot=-1.225051028293E-10
iode=47
t=383760


mu=3.986005E+14
omega_dot_e=7.2921151467E-5
n_0=np.sqrt(mu/(A*A*A))
tk=t-t_oe
n=n_0+delta_n
Mk=M_0+n*tk
Ek=Mk
print(Mk)
#for i in range(0,3):
 #   Ek =  Ek +(Mk-Ek+e*np.sin(Ek)/1-e*np.cos(Ek))

for i in range(0,3):
    Ek=Mk+e*np.sin(Ek)

vk=2*np.arctan(np.sqrt((1+e)/(1-e))*np.tan(Ek/2))
w=83.41104
phyk=vk+w
del_uk=c_us*np.sin(2*phyk) + c_uc*np.cos(2*phyk)
del_rk=c_rs*np.sin(2*phyk) + c_rc*np.cos(2*phyk)
del_ik=c_is*np.sin(2*phyk) + c_ic*np.cos(2*phyk)
uk=phyk+del_uk
rk=A*(1-e*np.cos(Ek)) +del_rk
ik=i_0+del_ik+idot*tk
print(ik)
x_kd=rk*np.cos(uk)
y_kd=rk*np.sin(uk)
omega_k=omega_0 + (omega_dot-omega_dot_e)*tk-(omega_dot_e*t_oe)
x_k=x_kd*np.cos(omega_k) - y_kd*np.cos(ik)*np.sin(omega_k)
y_k=x_kd*np.sin(omega_k) + y_kd*np.cos(ik)*np.cos(omega_k)
z_k=y_kd*np.sin(ik)

print(x_k)
print(y_k)
print(z_k)


