import pymap3d as pm
import numpy as np
import datetime
lat = 39.021
lon = -76.827
alt  = 19
x,y,z = pm.geodetic2ecef(lat,lon,alt)
X=np.array([x,y,z])
Y=np.array([-2.262803367450647801e+07,-1.107646130590583384e+07,8.796277366860926151e+06])
first_obs_time = datetime.datetime.strptime('2021 06 24 01 59 44', '%Y %m %d %H %M %S')
gps_week = 2163  # from the RINEX observation data
tow = 359676.783165  # from the RINEX observation data
gps_time = gps_week * 604800 + tow
system_time = datetime.datetime.utcnow().timestamp()
offset = gps_time - (first_obs_time.timestamp() + 18)
sat_off=-0.0001520831137896*299792458
print(sat_off)
res=sat_off-offset
print(offset)
print(res)
