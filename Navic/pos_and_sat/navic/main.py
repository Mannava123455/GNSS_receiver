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


sys.path.insert(0,'/navic')

from rinex_to_csv.r_to_csv import *
from str_to_float.funcs import *
from position.funcs import *
from conversions.funcs import *



rinex_file = "1.rnx"
output_file = 'data.csv'

rinex_to_csv(rinex_file, output_file)


remove_empty_rows('data.csv', 'updated.csv')

df = pd.read_csv('updated.csv')

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
        x, y, z = keplerian2ecef(dat)
        a,b,c=velocity(dat)
        pos_x.append(x)
        pos_y.append(y)
        pos_z.append(z)

        v_x.append(a)
        v_y.append(b)
        v_z.append(c)


        pos_x_list = [arr.tolist() for arr in pos_x]   # convert all NumPy arrays to lists
        pos_y_list = [arr.tolist() for arr in pos_y]   # convert all NumPy arrays to lists
        pos_z_list = [arr.tolist() for arr in pos_z]   # convert all NumPy arrays to lists
        position_x = [num for sublist in pos_x_list for num in sublist]
        position_y = [num for sublist in pos_y_list for num in sublist]
        position_z = [num for sublist in pos_z_list for num in sublist]

        v_x_list = [arr.tolist() for arr in v_x]   # convert all NumPy arrays to lists
        v_y_list = [arr.tolist() for arr in v_y]   # convert all NumPy arrays to lists
        v_z_list = [arr.tolist() for arr in v_z]   # convert all NumPy arrays to lists
        vel_x = [num for sublist in v_x_list for num in sublist]
        vel_y = [num for sublist in v_y_list for num in sublist]
        vel_z = [num for sublist in v_z_list for num in sublist]



x_pos = [list(arr) for arr in pos_x_list]
X= list(itertools.chain(*x_pos))
y_pos = [list(arr) for arr in pos_y_list]
Y= list(itertools.chain(*y_pos))
z_pos = [list(arr) for arr in pos_z_list]
Z= list(itertools.chain(*z_pos))

position = [[x1, y1, z1] for x1, y1, z1 in zip(X, Y, Z)]

v1 = [list(arr) for arr in v_x_list]
v_X= list(itertools.chain(*v1))
v2 = [list(arr) for arr in v_y_list]
v_Y= list(itertools.chain(*v2))
v3 = [list(arr) for arr in v_z_list]
v_Z= list(itertools.chain(*v3))

velocity = [[x2, y2, z2] for x2, y2, z2 in zip(v_X, v_Y, v_Z)]



print("position")
print(position)

print("velocity")
print(velocity)

#receiver points

lat = 39.021
lon = -76.827
alt  = 19


rx,ry,rz=geodetic_to_ecef(lon,lat,alt)
print(" ");
print("receiver coordinates with respect to receiver ");

print(rx)
print(ry)
print(rz)

with open('position.txt', 'w') as f:
    for item in position:
        f.write(f"{item}\n")

with open('velocity.txt', 'w') as f:
    for item in velocity:
        f.write(f"{item}\n")



