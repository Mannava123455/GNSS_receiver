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


def calSatPos(data, timeCor=False, iteration='Newton'):
    data=np.array(data)
    sats = np.zeros([data.shape[0],5])
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
                f = NR-e*np.sin(NR)-M  #function f(NR) = NR - e*sin(NR) - M 
                f1 = 1-e*np.cos(NR) # first order differentiation of f(NR)
                f2 = e*np.sin(NR) # second order diff of f(NR)
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
    return sats




"""
The parameters of rinex file

RINEX VERSION / TYPE: 3.04 N: GNSS NAV DATA G: GPS
PGM / RUN BY / DATE: JPS2RIN v.2.0.191 JAVAD GNSS 20210625 000625 UTC
LEAP SECONDS: 18
MARKER NAME: GODS
MARKER NUMBER: 40451M128
APPROX POSITION XYZ: 1130752.3120 -4831349.1180 3994098.9450
G27: This is the PRN (pseudo-random noise) number of the GPS satellite
2021 06 24 01 59 44: This is the date and time of the GPS data
-1.520831137896D-04: Clock correction with respect to GPS time
-6.139089236967D-12: Clock drift with respect to GPS time
0.000000000000D+00: Clock drift rate with respect to GPS time
1.500000000000D+01: IODE (Issue of Data, Ephemeris)
7.231250000000D+01: Crs (Radius Correction)
4.336252050875D-09: Delta n (Mean motion difference)
2.080850228679D+00: M0 (Mean anomaly at reference time)
3.596767783165D-06: Cuc (Argument of latitude, harmonic correction)
9.450974990614D-03: Eccentricity
-1.415610313416D-07: Cus (Sine of argument of latitude, harmonic correction)
5.153684047699D+03: sqrt(A) (Square root of the semi-major axis)
3.527840000000D+05: Toe (Time of ephemeris)
-1.676380634308D-07: Cic (Inclination, harmonic correction)
1.286603377064D+00: OMEGA0 (Longitude of ascending node at weekly epoch)
-1.862645149231D-08: Cis (Sine of inclination, harmonic correction)
9.755137728985D-01: i0 (Inclination angle at reference time)
3.894375000000D+02: CRC (Amplitude of orbit radius correction)
6.348804108489D-01: omega (Argument of perigee)
-8.337132989339D-09: OMEGADOT (Rate of right ascension)
1.871506527187D-10: IDOT (Rate of inclination angle)
1.000000000000D+00: Codes on L2 channel
2.163000000000D+03: GPS week number
0.000000000000D+00: L2 P data flag
2.000000000000D+00: SV accuracy (URA)
0.000000000000D+00: SV health
1.862645000000D-09: Tgd (Group delay)
1.500000000000D+01: Transmission time of message (seconds)
3.521400000000D+05: Fit interval (hours)
4.000000000000D+00: Time of clock (hours)
"""


