
import pytest
import xarray
from pytest import approx
import georinex as gr
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import math
import itertools





def keplerian2ecef(
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
    Ek = (Mk - e * np.sin(Mk))  # Eccentric anomaly
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
    Ek = (Mk - e * np.sin(Mk))  # Eccentric anomaly
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
    E_kdot = n/(1-sv["Eccentricity"].values*np.cos(Ek))
    v_kdot = (E_kdot*(np.sqrt(1-sv["Eccentricity"].values*sv["Eccentricity"].values)))/(1-sv["Eccentricity"].values*np.cos(Ek))
    d_ik_dt = sv["IDOT"].values + 2*v_kdot*(sv["Cis"].values*np.cos(2*PhiK)-sv["Cic"].values*np.sin(2*PhiK))
    u_kdot = v_kdot+2*v_kdot*(sv["Cus"].values*np.cos(2*PhiK) - sv["Cus"].values*np.sin(2*PhiK))
    r_kdot =sv["Eccentricity"].values*A*E_kdot*np.sin(Ek) + 2*v_kdot*(sv["Crs"].values*np.cos(2*PhiK) -sv["Crc"].values*np.sin(2*PhiK))
    omega_kdot = sv["OmegaDot"].values - omega_e
    x_kdd = r_kdot*np.cos(uk) - rk*u_kdot*np.sin(uk)
    y_kdd = r_kdot*np.sin(uk) + rk*u_kdot*np.cos(uk)

    x_kdot = -Xk1*omega_kdot*np.sin(OmegaK) + x_kdd*np.cos(OmegaK) - y_kdd*np.sin(OmegaK)*np.cos(ik) - Yk1*(omega_kdot*np.cos(OmegaK)*np.cos(ik) -(d_ik_dt)*np.sin(OmegaK)*np.sin(ik))


    y_kdot = -Xk1*omega_kdot*np.cos(OmegaK) + x_kdd*np.sin(OmegaK) + y_kdd*np.cos(OmegaK)*np.cos(ik) - Yk1*(omega_kdot*np.sin(OmegaK)*np.cos(ik) +(d_ik_dt)*np.cos(OmegaK)*np.sin(ik))


    z_kdot =  Yk1*(d_ik_dt)*np.cos(ik)+y_kdd*np.sin(ik)

    return x_kdot,y_kdot,z_kdot
    


    








