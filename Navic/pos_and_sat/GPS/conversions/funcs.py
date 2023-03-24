import math

a = 6378137.0   	# Earth's semimajor axis in meters
b = 6356752.31424518	# Earth's semiminor axis in meters
e2 = (a**2 - b**2) / b**2

def spherical_to_ecef(lon, lat, alt):
    
    lon_rad = math.radians(lon)
    lat_rad = math.radians(lat)
    cos_lat = math.cos(lat_rad)
    sin_lat = math.sin(lat_rad)
    cos_lon = math.cos(lon_rad)
    sin_lon = math.sin(lon_rad)
    f = (a**2 - b**2) / a**2
    e2 = (a**2 - b**2) / b**2
    N = a / math.sqrt(1 - e2 * sin_lat**2)
    x = (N + alt) * cos_lat * cos_lon
    y = (N + alt) * cos_lat * sin_lon
    z = (N * (1 - e2) + alt) * sin_lat
    return x, y, z


def ecef_to_spherical(x, y, z):

    r = math.sqrt(x**2 + y**2 + z**2)
    lon = math.atan2(y, x)
    lat = math.asin(z / r)
    N = a / math.sqrt(1 - e2 * math.sin(lat)**2)
    alt = r / math.cos(lat) - N
    lon_deg = math.degrees(lon)
    lat_deg = math.degrees(lat)
    return lon_deg, lat_deg, alt


def geodetic_to_ecef(lon, lat, alt):

    lon_rad = math.radians(lon)
    lat_rad = math.radians(lat)
    cos_lat = math.cos(lat_rad)
    sin_lat = math.sin(lat_rad)
    cos_lon = math.cos(lon_rad)
    sin_lon = math.sin(lon_rad)
    f = (a**2 - b**2) / a**2
    e2 = (a**2 - b**2) / b**2
    N = a / math.sqrt(1 - e2 * (sin_lat**2))
    x = (N + alt) * cos_lat * cos_lon
    y = (N + alt) * cos_lat * sin_lon
    z = (N * (1 - e2) + alt) * sin_lat
    return x, y, z


def ecef_to_geodetic(x, y, z):

    r = math.sqrt(x**2 + y**2 + z**2)
    lon = math.atan2(y, x)
    lat_prev = math.atan2(z, math.sqrt(x**2 + y**2))
    while True:
        N = a / math.sqrt(1 - e2 * math.sin(lat_prev)**2)
        lat = math.atan2(z + N * e2 * math.sin(lat_prev), math.sqrt(x**2 + y**2))
        if abs(lat - lat_prev) < 1e-10:
            break
        lat_prev = lat
    alt = r / math.cos(lat) - N
    lon_deg = math.degrees(lon)
    lat_deg = math.degrees(lat)
    return lon_deg, lat_deg, alt
    

def geodetic_to_spherical(lon, lat, alt):

    N = a / math.sqrt(1 - e2 * math.sin(math.radians(lat))**2)
    r = (N + alt) * math.cos(math.radians(lat))
    x = r * math.cos(math.radians(lon))
    y = r * math.sin(math.radians(lon))
    z = (N * (1 - e2) + alt) * math.sin(math.radians(lat))
    return x, y, z

def spherical_to_geodetic(x, y, z):

    r = math.sqrt(x**2 + y**2 + z**2)
    lon = math.atan2(y, x)
    lat_prev = math.atan2(z, math.sqrt(x**2 + y**2))
    while True:
        N = a / math.sqrt(1 - e2 * math.sin(lat_prev)**2)
        lat = math.atan2(z + N * e2 * math.sin(lat_prev), math.sqrt(x**2 + y**2))
        if abs(lat - lat_prev) < 1e-10:
            break
        lat_prev = lat
    alt = r / math.cos(lat) - N
    lon_deg = math.degrees(lon)
    lat_deg = math.degrees(lat)
    return lon_deg, lat_deg, alt


