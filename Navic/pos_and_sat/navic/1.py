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

sys.path.insert(0,'/navic')
from rinex_to_csv.funcs import *
from position.funcs import *
from velocity.funcs import *
from rinexread.funcs import *
file="./data/updated.csv"
data=navic(file)
print(data)
