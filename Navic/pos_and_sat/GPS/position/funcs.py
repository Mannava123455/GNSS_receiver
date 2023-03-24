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

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument('--file', type=str, default = None)
parser.add_argument('--timeCor', type=bool, default = False)
parser.add_argument('--iteration', type=str, default = 'Newton')
args = parser.parse_args()

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
        E=M+e*np.sin(M)
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






def position_of_sat(
    sv: xarray.Dataset,
) -> tuple[xarray.DataArray, xarray.DataArray, xarray.DataArray]:

    GM = 3.986004418*np.power(10.0,14)  # [m^3 s^-2]   Mean anomaly at tk
    omega_e = 7.2921151467*np.power(10.0,-5)  # [rad s^-1]  Mean angular velocity of Earth
    A = sv["sqrtA"].values * sv["sqrtA"].values
    n0 = np.sqrt(GM / A ** 3)  # computed mean motion
    T = 2*np.pi / n0  # Satellite orbital period
    n = n0 + sv["DeltaN"].values  # corrected mean motion
    if sv.svtype[0] == "E":
        weeks = sv["GALWeek"].values - 1024
    elif sv.svtype[0] == "G":
        weeks = sv["GPSWeek"].values
    else:
        raise ValueError(f"Unknown system type {sv.svtype[0]}")
    weeks = np.atleast_1d(weeks).astype(float)
    Toe = np.atleast_1d(sv["Toe"].values).astype(float)
    Transtime = np.atleast_1d(sv["TransTime"].values).astype(float)
    e = sv["Eccentricity"].values
    T0 = [datetime(1980, 1, 6) + timedelta(weeks=week) for week in weeks]
    z =Transtime - Toe
    tk = np.empty(z.size,dtype=float)
    Mk = (sv["M0"].values + n * tk)  # Mean Anomaly
    Ek = (Mk + e * np.sin(Mk))  # Eccentric anomaly
    nuK = np.arctan2(np.sqrt(1 - e ** 2) * np.sin(Ek), np.cos(Ek) - e)
    PhiK = nuK + sv["omega"].values  # argument of latitude
    duk = sv["Cuc"].values * np.cos(2 * PhiK) + sv["Cus"].values * np.sin(
        2 * PhiK
    )  # argument of latitude correction
    uk = PhiK + duk  # corred argument of latitude
    # %% inclination (same)
    dik = sv["Cic"].values * np.cos(2 * PhiK) + sv["Cis"].values * np.sin(
        2 * PhiK
    )  # inclination correction
    ik = sv["Io"].values + sv["IDOT"].values * tk + dik  # corrected inclination
    # %% radial distance (same)
    drk = sv["Crc"].values * np.cos(2 * PhiK) + sv["Crs"].values * np.sin(
        2 * PhiK
    )  # radial correction
    rk = A * (1 - e * np.cos(Ek)) + drk  # corrected radial distance
    # %% right ascension  (same)
    OmegaK = sv["Omega0"].values + (sv["OmegaDot"].values - omega_e) * tk - omega_e * Toe
    # %% transform
    Xk1 = rk * np.cos(uk)
    Yk1 = rk * np.sin(uk)
    X = Xk1 * np.cos(OmegaK) - Yk1 * np.sin(OmegaK) * np.cos(ik)
    Y = Xk1 * np.sin(OmegaK) + Yk1 * np.cos(OmegaK) * np.cos(ik)
    Z = Yk1 * np.sin(ik)
    return X, Y, Z






def navic(file):
    df = pd.read_csv(file)
    sv = [0]*121#df ['sv'].tolist()
    time=[0]*121
    month=[0]*121
    day =[0]*121
    hour=[0]*121
    minute =[0]*121
    second=[0]*121
    SVclockBias = df['SVclockBias'].tolist()
    SVclockDrift = df['SVclockDrift'].tolist()
    SVclockDriftRate = df['SVclockDriftRate'].tolist()
    IODEC = df['IODEC'].tolist()
    Crs = df['Crs'].tolist()
    DeltaN = df['DeltaN'].tolist()
    M0 = df['M0'].tolist()
    Cuc = df['Cuc'].tolist()
    Eccentricity = df['Eccentricity'].tolist()
    Cus = df['Cus'].tolist()
    sqrtA = df['sqrtA'].tolist()
    Toe = df['Toe'].tolist()
    Cic = df['Cic'].tolist()
    Omega0 = df['Omega0'].tolist()
    Cis = df['Cis'].tolist()
    Io = df['Io'].tolist()
    Crc = df['Crc'].tolist()
    omega = df['omega'].tolist()
    OmegaDot = df['OmegaDot'].tolist()
    IDOT = df['IDOT'].tolist()
    codesL2 = [0]*121
    BDTWeek = df['BDTWeek'].tolist()
    L2flag = [0]*121
    URA = df['URA'].tolist()
    health = df['health'].tolist()
    TGD = df['TGD'].tolist()
    IODC =[0]*121
    TransTime = df['TransTime'].tolist()
    
    
    data = list([[a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,aa,ab,ac,ad,ae,af,ag,ah,ai,] for a, b, c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,aa,ab,ac,ad,ae,af,ag,ah,ai in list(zip(sv,time,month,day,hour,minute,second,SVclockBias,SVclockDrift,SVclockDriftRate,IODEC,Crs,DeltaN,M0,Cuc,Eccentricity,Cus,sqrtA,Toe,Cic,Omega0,Cis,Io,Crc,omega,OmegaDot,IDOT,codesL2,BDTWeek,L2flag,URA,health,TGD,IODC,TransTime))])
    return data
