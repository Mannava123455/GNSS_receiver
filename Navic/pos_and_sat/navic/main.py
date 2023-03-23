import georinex as gr
import pandas as pd
import sys
import os
import math
import itertools
import numpy as np
import pytest
import xarray
from pytest import approx
from datetime import datetime, timedelta
import pymap3d as pr


sys.path.insert(0,'/navic')

from rinex_to_csv.r_to_csv import *
from str_to_float.funcs import *
from position.funcs import *
from conversions.funcs import *



rinex_file = "./data/gps.rnx"
output_file = './data/data.csv'

rinex_to_csv(rinex_file, output_file)


remove_empty_rows('./data/data.csv', './data/updated.csv')

df = pd.read_csv('./data/updated.csv')

GPSWeek = df['GPSWeek'].tolist()
Toe = df['Toe'].tolist()
Eccentricity= df['Eccentricity'].tolist()
sqrtA = df['sqrtA'].tolist()
Cic = df['Cic'].tolist()
Crc = df['Crc'].tolist()
Cis = df['Cis'].tolist()
Crs = df['Crs'].tolist()
Cuc = df['Cuc'].tolist()
Cus = df['Cus'].tolist()
DeltaN = df['DeltaN'].tolist()
Omega0 = df['Omega0'].tolist()
omega = df['omega'].tolist()
Io = df['Io'].tolist()
OmegaDot = df['OmegaDot'].tolist()
IDOT = df['IDOT'].tolist()
M0 = df['M0'].tolist()
TransTime = df['TransTime'].tolist()


pos_x=[]
pos_y=[]
pos_z=[]
v_x=[]
v_y=[]
v_z=[]
for i in range(0,len(M0)):
        TGPS0 = datetime(1980, 1, 6)
        sv = {
          "GPSWeek": GPSWeek[i],
          "Toe":Toe[i],
          "Eccentricity": Eccentricity[i],
          "sqrtA": sqrtA[i],
          "Cic": Cic[i],
          "Crc": Crc[i],
          "Cis": Cis[i],
          "Crs": Crs[i],
          "Cuc": Cuc[i],
          "Cus": Cus[i],
          "DeltaN": DeltaN[i],
          "Omega0": Omega0[i],
          "omega": omega[i],
          "Io": Io[i],
          "OmegaDot": OmegaDot[i],
          "IDOT": IDOT[i],
          "M0": M0[i],
          "TransTime":TransTime[i]
          }

        time = TGPS0 + timedelta(weeks=GPSWeek[i], seconds=4.03272930e5)
        dat = xarray.Dataset(
             sv,
             attrs={"svtype": "G"},
             coords={"time": [time]},
         )


        x, y, z = position_of_sat(dat)
        a,b,c=velocity(dat)
        pos_x.append(x)
        pos_y.append(y)
        pos_z.append(z)

        v_x.append(a)
        v_y.append(b)
        v_z.append(c)

x1 = [a.tolist()[0] for a in pos_x]
x2 = [a.tolist()[0] for a in pos_y]
x3 = [a.tolist()[0] for a in pos_z]
position = list([(a, b, c) for a, b, c in list(zip(x1, x2, x3))])
np.savetxt("./data/pos_main.txt",position)

v1 = [a.tolist()[0] for a in v_x]
v2 = [a.tolist()[0] for a in v_y]
v3 = [a.tolist()[0] for a in v_z]
velocity = list([(a, b, c) for a, b, c in list(zip(v1, v2, v3))])
np.savetxt("./data/vel_main.txt",velocity)




lat = 39.021
lon = -76.827
alt  = 19
rx,ry,rz=pr.ecef2aer(x1, x2, x3, lat, lon, alt, ell=None, deg=True)
spherical = [[x2, y2, z2] for x2, y2, z2 in zip(rx, ry, rz)]
np.savetxt("./data/pos_main_sp.txt",spherical)
np.savetxt("./data/pos_main_sp.csv",spherical)




