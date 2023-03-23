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

def readRinexN(file):
    data = {}
    with open(file,'rt') as f:
        foundend = 0
        idx = 0
        for line in f:
            a = line.split(' ')
            if 'END' in a:
                foundend = 1
                continue
            if foundend==0:
                continue
            b = [x for x in a if x!='']
            try:
                b.remove('\n')
            except:
                pass
            if len(b)!=4:
                idx += 1
                data[str(idx)] = b
            else:
                for each in b:
                    data[str(idx)].append(each)
                    
    data2 = np.zeros([len(data),38])
    outercount = 0
    for (k,v) in data.items(): 
        count = 0
        for each in v:
            if 'D' in each:
                tmp = each.split('D')
                tmp = float(tmp[0])*np.power(10.0,float(tmp[1]))
            else:
                tmp = float(each)
            data2[outercount,count] = tmp
            count += 1
        outercount += 1
    return data, data2

def readRinexN302(file):
    data = {}
    with open(file,'r') as f:
        foundend = 0
        idx = 0
        for line in f:
            a = line.split(' ')
            if 'END' in a:
                foundend = 1
                continue
            if foundend==0:
                continue
            b = [x for x in a if x!='']
            try:
                b.remove('\n')
            except:
                pass
            if len(b)!=4:
                idx += 1
                data[str(idx)] = b
            else:
                for each in b:
                    data[str(idx)].append(each)
                    
    data2 = np.zeros([len(data),38])
    outercount = 0
    for (k,v) in data.items(): 
        count = 0
        for each in v:
            if 'D' in each:
                tmp = each.split('D')
                tmp = float(tmp[0])*np.power(10.0,float(tmp[1]))
            else:
                if 'G' in each:
                    tmp = float(each.split('G')[1])
                elif 'C' in each:
                    tmp = float(each.split('C')[1])
                else:
                    tmp = float(each)
            data2[outercount,count] = tmp
            count += 1
        outercount += 1
    return data, data2

def calSatPos(data, timeCor=False, iteration='Newton'):
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





def velocity(
    sv: xarray.Dataset,
) -> tuple[xarray.DataArray, xarray.DataArray, xarray.DataArray]:
    GM = 3.986004418e14  # [m^3 s^-2]   Mean anomaly at tk
    omega_e = 7.2921151467e-5  # [rad s^-1]  Mean angular velocity of Earth
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
    E_kdot = n*(1-e*np.cos(Ek))

    v_kdot = (E_kdot*(np.sqrt(1-e*e)))/(1-e*np.cos(Ek))

    d_ik_dt = sv["IDOT"].values + 2*v_kdot*(sv["Cis"].values*np.cos(2*PhiK)-sv["Cic"].values*np.sin(2*PhiK))

    u_kdot = v_kdot+2*v_kdot*(sv["Cus"].values*np.cos(2*PhiK) - sv["Cuc"].values*np.sin(2*PhiK))

    r_kdot =e*A*E_kdot*np.sin(Ek) + 2*v_kdot*(sv["Crs"].values*np.cos(2*PhiK) -sv["Crc"].values*np.sin(2*PhiK))

    omega_kdot = sv["OmegaDot"].values - 2*omega_e

    x_kdd = r_kdot*np.cos(uk) - rk*u_kdot*np.sin(uk)

    y_kdd = r_kdot*np.sin(uk) + rk*u_kdot*np.cos(uk)


    x_kdot = -Xk1*omega_kdot*np.sin(OmegaK) + x_kdd*np.cos(OmegaK) - y_kdd*np.sin(OmegaK)*np.cos(ik) - Yk1*(omega_kdot*np.cos(OmegaK)*np.cos(ik) -(d_ik_dt)*np.sin(OmegaK)*np.sin(ik))


    y_kdot = Xk1*omega_kdot*np.cos(OmegaK) + x_kdd*np.sin(OmegaK) + y_kdd*np.cos(OmegaK)*np.cos(ik) - Yk1*(omega_kdot*np.sin(OmegaK)*np.cos(ik) +(d_ik_dt)*np.cos(OmegaK)*np.sin(ik))


    z_kdot =  Yk1*(d_ik_dt)*np.cos(ik)+y_kdd*np.sin(ik)

    return x_kdot,y_kdot,z_kdot
    


    








