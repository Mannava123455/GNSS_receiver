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
import pyproj
import pymap3d as pr
import argparse
import pymap3d as pr




parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument('--file', type=str, default = None)
parser.add_argument('--timeCor', type=bool, default = False)
parser.add_argument('--iteration', type=str, default = 'Newton')
args = parser.parse_args()


sys.path.insert(0,'/navic')

from rinex_to_csv.r_to_csv import *
from str_to_float.funcs import *
from position.funcs import *
from conversions.funcs import *



rawdata,data = readRinexN302(args.file)
satp = calSatPos(data,timeCor=args.timeCor,iteration=args.iteration)
pos = satp.tolist()
posi=[]
X=[]
Y=[]
Z=[]
for sublist in pos:
    # Check if the sublist contains nan values
    if np.isnan(sublist).any():
        continue  # Skip this sublist and move on to the next one
    else:
        posi.append(sublist)  # Add this sublist to the new list
for sublist in posi:
    sublist.pop()
np.savetxt('./data/pos_main1.txt',posi,delimiter=',')
np.savetxt('./data/pos_main1.csv',posi,delimiter=',')

for sublist in posi:
    sublist.pop(0)
for sublist in posi:
    X.append(sublist[0])
    Y.append(sublist[1])
    Z.append(sublist[2])
lat = 39.021
lon = -76.827
alt  = 19
rx,ry,rz=pr.ecef2aer(X,Y,Z,lat,lon,alt,ell=None,deg=True)
spherical=[[i,j,k] for i,j,k in zip(rx,ry,rz)]
np.savetxt("./data/pos_main1_sp.txt",spherical)
np.savetxt("./data/pos_main1_sp.csv",spherical)
