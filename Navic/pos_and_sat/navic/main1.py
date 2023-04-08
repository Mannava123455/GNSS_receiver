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
parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument('--file', type=str, default = None)
parser.add_argument('--timeCor', type=bool, default = False)
parser.add_argument('--iteration', type=str, default = 'Newton')
args = parser.parse_args()
sys.path.insert(0,'/navic')
from rinex_to_csv.funcs import *
from position.funcs import *
from velocity.funcs import *
from rinexread.funcs import *
rinex_file = "./data/navic.rnx"
output_file = './data/data.csv'
rinex_to_csv(rinex_file, output_file)
remove_empty_rows('./data/data.csv', './data/updated.csv')
file="./data/updated.csv"
data=navic(file)
satp = calSatPos(data,timeCor=args.timeCor,iteration=args.iteration)
satv = calSatvel(data,timeCor=args.timeCor,iteration=args.iteration)
pos = satp.tolist()
vel = satv.tolist()
for sublist in pos:
    sublist.pop()
for sublist in pos:
    sublist.pop(0)
for sublist in vel:
    sublist.pop()
for sublist in vel:
    sublist.pop()
X=[]
Y=[]
Z=[]
np.savetxt('./data/pos_main1.txt',pos,delimiter=',')
np.savetxt('./data/pos_main1.csv',pos,delimiter=',')
np.savetxt('./data/vel_main1.txt',vel,delimiter=',')
np.savetxt('./data/ve1_main1.csv',vel,delimiter=',')
for sublist  in pos:
      X.append(sublist[0])
      Y.append(sublist[1])
      Z.append(sublist[2])
lat = 17.5910
lon = 78.1213
alt = 19
rx,ry,rz=pr.ecef2aer(X,Y,Z,lat,lon,alt,ell=None,deg=True)
spherical=[[i,j,k] for i,j,k in zip(rx,ry,rz)]
np.savetxt("./data/pos_main1_sp.txt",spherical)
np.savetxt("./data/pos_main1_sp.csv",spherical)

