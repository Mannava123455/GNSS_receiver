import numpy as np
import math


def geo_to_ecef(lon_deg, lat_deg, elev_m):
    # Convert longitude and latitude to radians
    lon_rad = math.radians(lon_deg)
    lat_rad = math.radians(lat_deg)

    # Calculate radius of curvature in prime vertical and distance from Earth's center to surface at given latitude
    a = 6378137.0  # semi-major axis of WGS84 ellipsoid
    f = 1 / 298.257223563  # flattening of WGS84 ellipsoid
    b = a * (1 - f)  # semi-minor axis of WGS84 ellipsoid
    e_sq = (a**2 - b**2) / a**2  # eccentricity squared of WGS84 ellipsoid
    N = a / math.sqrt(1 - e_sq * math.sin(lat_rad)**2)
    R = N * (1 - e_sq) / (1 - e_sq * math.sin(lat_rad) ** 2)

    # Calculate ECEF coordinates
    x = (R + elev_m) * math.cos(lat_rad) * math.cos(lon_rad)
    y = (R + elev_m) * math.cos(lat_rad) * math.sin(lon_rad)
    z = (R * (1 - e_sq) + elev_m) * math.sin(lat_rad)

    return x, y, z


print(geo_to_ecef(39.01,-76.827,19))


