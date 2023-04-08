
import pytest
import xarray
from pytest import approx
import georinex as gr
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import math
import itertools
import argparse


GM = 3.986005*np.power(10.0,14)
c = 2.99792458*np.power(10.0,8)
omegae_dot = 7.2921151467*np.power(10.0,-5)

def calSatvel(data, timeCor=False, iteration='Newton'):
    data=np.array(data)
    sats = np.zeros([data.shape[0],5])
    satv = np.zeros([data.shape[0],5])

    for j in range(data.shape[0]):
        ## load variables
        A = np.power(data[j,17],2) 
        toe = data[j,18] # Time of Ephemeris
        tsv = data[j,18]
        tk = tsv - toe
        n0 = np.sqrt(GM/np.power(A,3)) #
        dn = data[j,12]
        n = n0 + dn
        m0 = data[j,13]
        M = m0+n*tk
        af0 = data[j,7]
        af1 = data[j,8]
        w = data[j,24]
        cuc = data[j,14] 
        cus = data[j,16]
        crc = data[j,23]
        crs = data[j,11]
        cis = data[j,21]
        cic = data[j,19]
        i0 = data[j,22]
        idot = data[j,26]
        omg0 = data[j,20]
        odot = data[j,25] 
        e = data[j,15] # Eccentricity
        
        ## time correction
        if timeCor == True:
            NRnext = 0
            NR = 1
            m = 1
            while np.abs(NRnext-NR)>np.power(10.0,-16):
                NR = NRnext
                f = NR-e*np.sin(NR)-M
                f1 = 1-e*np.cos(NR)
                f2 = e*np.sin(NR)
                if iteration=='Householder':
                    NRnext = NR - f/(f1-(f2*f/(2*f1)))
                else:
                    NRnext = NR - f/f1
                m += 1
            
            E = NRnext
            
            F = -2*np.sqrt(GM)/np.power(c,2)
            delta_tr = F*e*np.sqrt(A)*np.sin(E)
            delta_tsv = af0+af1*(tsv-toe)+delta_tr
            t = tsv-delta_tsv
            tk = t-toe
            M = m0+n*tk
        else:
            NRnext = 0
            NR = 1
            m = 1
            while np.abs(NRnext-NR)>np.power(10.0,-16):
                NR = NRnext
                f = NR-e*np.sin(NR)-M
                f1 = 1-e*np.cos(NR)
                f2 = e*np.sin(NR)
                if iteration=='Householder':
                    NRnext = NR - f/(f1-(f2*f/(2*f1)))
                else:
                    NRnext = NR - f/f1
                m += 1

        E = NRnext
        #E=M+e*np.sin(M)
        v = np.arctan2(np.sqrt(1-np.power(e,2))*np.sin(E),np.cos(E)-e)
        phi = v + w
        u = phi + cuc*np.cos(2*phi) + cus*np.sin(2*phi)
        r = A*(1-e*np.cos(E)) + crc*np.cos(2*phi) + crs*np.sin(2*phi)
        i = i0 + idot*tk
        Omega = omg0 + (odot-omegae_dot)*tk - omegae_dot*toe
        x1 = np.cos(u)*r
        y1 = np.sin(u)*r
        
        sats[j,0] = data[j,0]
        sats[j,1] = x1*np.cos(Omega) - y1*np.cos(i)*np.sin(Omega)
        sats[j,2] = x1*np.sin(Omega) + y1*np.cos(i)*np.cos(Omega)
        sats[j,3] = y1*np.sin(i)




        E_dot=n/(1-e*np.cos(E))
        v_dot=(E_dot*np.sqrt(1-e*e))/(1-e*np.cos(E))
        di_dt=idot
        di_dt = idot + 2*v_dot*(cis*np.cos(2*phi)-cic*np.sin(2*phi))
        u_dot=v_dot + 2*v_dot*(cus*np.cos(2*phi) - cuc*np.sin(2*phi))
        r_dot=e*A*E_dot*np.sin(E) + 2*v_dot*(crs*np.cos(2*phi) - crc*np.sin(2*phi))
        Omega_dot=(odot-omegae_dot)

        x_kdd = r_dot*np.cos(u) - r*u_dot*np.sin(u)
        y_kdd = r_dot*np.sin(u) + r*u_dot*np.cos(u)
        x_kdot = -x1*Omega_dot*np.sin(Omega) + x_kdd*np.cos(Omega) - y_kdd*np.sin(Omega)*np.cos(i) - y1*(Omega_dot*np.cos(Omega)*np.cos(i) -(di_dt)*np.sin(Omega)*np.sin(i))


        y_kdot = x1*Omega_dot*np.cos(Omega) + x_kdd*np.sin(Omega) + y_kdd*np.cos(Omega)*np.cos(i) - y1*(Omega_dot*np.sin(Omega)*np.cos(i) +(di_dt)*np.cos(Omega)*np.sin(i))


        z_kdot =  y1*(di_dt)*np.cos(i)+y_kdd*np.sin(i)

        satv[j,0] = x_kdot
        satv[j,1] = y_kdot
        satv[j,2] = z_kdot
    return satv
