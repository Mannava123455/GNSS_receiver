import numpy as np
import matplotlib as plt
import astropy.units as u

G = 6.6725*10**-11   # Newtonian Gravitational Constant
c = 63197.8       # Speed of light in au/yr units

M = 5.98*10**24          # Mass of the Earth in kg units
R = 6378.165*10**3       # Earth's equatorial radius in m
h = 200*10**3            # Height of the satellite above the Earth in m
a = 6644.5828*10**3      # semi major axis in m (...x 10^3 m)
e = 0.01                 # Orbit's eccentricity
i = 63*u.degree          # Orbit plane inclination
Omega = 40*u.degree      # Ascendent node angle
omega = 30*u.degree      # Argument of the pericenter
t_0 = 89.84*60   # Epoch in seconds  (... x 60 sec)
t_f = 89.84*60   # Arbitrary time    (... x 60 sec)

n = np.sqrt(G*M/a**3)     # Mean motion

m = n*(t_f-t_0)


f = lambda x: x-0.01*np.sin(x)-m
f_prime = lambda x: 1-0.01*np.cos(x)
newton_raphson = m - (f(m))/(f_prime(m))
print("newton_raphson =", newton_raphson)


r = a*(1-e*np.cos(newton_raphson))
print("r =", r)

X = a*(np.cos(newton_raphson)-e)

Y = a*np.sqrt(1-e**2)*np.sin(newton_raphson)

Z = 0


v_x = (np.sqrt(G*M*a)/r)*np.sin(newton_raphson)

v_y = (np.sqrt(G*M*a*(1-e**2))/r)*np.cos(newton_raphson)

v_z = 0


p_1 = np.cos(omega)*np.cos(Omega) - np.sin(omega)*np.sin(Omega)*np.cos(i)

p_2 = np.cos(omega)*np.sin(Omega) + np.sin(omega)*np.cos(Omega)*np.cos(i)

p_3 = np.sin(omega)*np.sin(i)

q_1 = - np.sin(omega)*np.cos(Omega) - np.cos(omega)*np.sin(Omega)*np.cos(i)

q_2 = - np.sin(omega)*np.sin(Omega) + np.cos(omega)*np.cos(Omega)*np.cos(i)

q_3 = np.cos(omega)*np.sin(i)

w_1 = np.sin(Omega)*np.sin(i)

w_2 = - np.cos(Omega)*np.sin(i) 

w_3 = np.cos(i)


r_1 = np.matrix([[X], [Y], [Z]])

print("r_1 = ", r_1)

v_1 = np.matrix([[v_x], [v_y], [v_z]])

print("v_1 = ", v_1)


P = np.matrix([[p_1, q_1, w_1], [p_2, q_2, w_2], [p_3, q_3, w_3]])

print("P = ", P)


R_1 = P*r_1

print("R_1 = ", R_1)


V_1 = P*v_1

print("V_1 = ", V_1)


h = r - R

print("h = ", h)
