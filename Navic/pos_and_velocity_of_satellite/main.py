import numpy as np

# input parameters
PRN=11
c_rs=-0.965625000000E+01
delta_n=0.583845748090E-08 
M_o=-0.286954703389E+01
c_uc=-0.379979610443E-06 
e=0.167867515702E-01
c_us=0.277347862720E-05 
A1=0.515375480270E+04
t_oe=0.000000000000E+00 
c_ic=0.199303030968E-06
omega_o=-0.657960408566E+00
c_is=0.173225998878E-06
i_o=0.903782727230E+00
c_rc=0.293218750000E+03
omega=0.173129682312E+01
omega_dot=-0.868929051526E-08
idot=0.789318592573E-10
gpsweek=0.198300000000E+04
t=383760


R_E =  6378137.0 #meters
j_2 = 0.0010826262


#computations

A=A1*A1
mu=3.986005E+14# × 1014
omega_e_dot=7.2921151467E-5
n_o=np.sqrt(mu/(A*A*A))

t_k=t-t_oe

if(t_k>302400):
    t_k=t_k-604800

elif(t_k<-302400):
    t_k=t_k+604800
else:
    t_k=t_k;

n=n_o+delta_n
M_k=M_o+n*t_k

#compute E_K

E_k=M_k
for i in range(0,3):
    E_k=E_k+ (M_k - E_k + e*np.sin(E_k))/(1-e*np.cos(E_k))

#compute true anomaly

v_k=2*np.arctan(np.sqrt((1+e)/(1-e))*np.tan(E_k/2))
w=np.pi  # argument of perigree for circular orbits is 0 
phy_k=v_k+w

del_u_k = c_us*np.sin(2*phy_k) + c_uc*np.cos(2*phy_k)
del_r_k = c_rs*np.sin(2*phy_k) + c_rc*np.cos(2*phy_k)
del_i_k = c_is*np.sin(2*phy_k) + c_ic*np.cos(2*phy_k)

u_k=phy_k + del_u_k
r_k=A*(1-e*np.cos(E_k))+del_r_k
i_k=i_o+del_i_k + idot*t_k
x_kd=r_k*np.cos(u_k)
y_kd=r_k*np.sin(u_k)
omega_k=omega_o + (omega_dot - omega_e_dot)*t_k - omega_e_dot*t_oe
x_k=x_kd*np.cos(omega_k) - y_kd*np.cos(i_k)*np.sin(omega_k)
y_k=x_kd*np.sin(omega_k) + y_kd*np.cos(i_k)*np.cos(omega_k)
z_k=y_kd*np.sin(i_k)
print(x_k)
print(y_k)
print(z_k)

#compute velocity

E_k_dot = n/(1-e*np.cos(E_k))

v_k_dot = E_k_dot*(np.sqrt(1-e*e))/(1-e*np.cos(E_k))

d_i_k_dt = (idot) + 2*v_k_dot*(c_is*np.cos(2*phy_k) - c_ic*np.sin(2*phy_k))

u_k_dot = v_k_dot + 2*v_k_dot*(c_us*np.cos(2*phy_k) - c_uc*np.sin(2*phy_k))

r_k_dot=e*A*E_k_dot*np.sin(E_k) + 2*v_k_dot*(c_rs*np.cos(2*phy_k) - c_rc*np.sin(2*phy_k))

omega_k_dot=omega_dot - omega_e_dot

x_k_d = r_k_dot*np.cos(u_k) - r_k*u_k_dot*np.sin(u_k)

y_k_d = r_k_dot*np.sin(u_k) - r_k*u_k_dot*np.cos(u_k)

x_k_dot = - x_k_d*omega_k_dot*np.sin(omega_k) + x_k_d*np.cos(omega_k) - y_k_d*np.sin(omega_k)*np.cos(i_k) - y_k_d*(omega_k_dot*np.cos(omega_k)*np.cos(i_k) -(d_i_k_dt)*np.sin(omega_k)*np.sin(i_k))

y_k_dot = x_k_d*omega_k_dot*np.cos(omega_k) + x_k_d*np.sin(omega_k) + y_k_d*np.cos(omega_k)*np.cos(i_k) - y_k_d*(omega_k_dot*np.sin(omega_k)*np.cos(i_k) + (d_i_k_dt)*np.cos(omega_k)*np.sin(i_k))

z_k_dot = y_k_d*(d_i_k_dt)*np.cos(i_k) + y_k_d*np.sin(i_k)

print("Velocity")
print(x_k_dot)
print(y_k_dot)
print(z_k_dot)

#compute acceleration 

F = -1.5*j_2*(mu/r_k*r_k)*(R_E/r_k)*(R_E/r_k)

x_a = -mu*(x_k/(r_k*r_k*r_k)) + F*((1-5*((z_k*z_k/r_k*r_k)))*(x_k/r_k)) + 2*y_k_dot*omega_e_dot + x_k*omega_e_dot*omega_e_dot


y_a = - mu*(y_k/(r_k*r_k*r_k)) + F*((1-5*((z_k*z_k/r_k*r_k)))*(y_k/r_k)) + 2*x_k_dot*omega_e_dot + y_k*omega_e_dot*omega_e_dot


z_a = - mu*(z_k/(r_k*r_k*r_k)) + F*((3-5*((z_k*z_k/r_k*r_k)))*(z_k/r_k))


print("acceleration")
print(x_a)
print(y_a)
print(z_a)





















