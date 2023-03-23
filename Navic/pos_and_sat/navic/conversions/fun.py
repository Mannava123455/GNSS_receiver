import pyproj

# Define coordinate systems
geod = pyproj.Geod(ellps='WGS84')  # Geodetic coordinate system
ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')  # ECEF coordinate system

# Convert spherical coordinates to ECEF
def spherical_to_ecef(lon, lat, alt):
    x, y, z = pyproj.transform(geod, ecef, lon, lat, alt, radians=True)
    return x, y, z

# Convert geodetic coordinates to ECEF
def geodetic_to_ecef(lon, lat, alt):
    x, y, z = pyproj.transform(geod, ecef, lon, lat, alt)
    return x, y, z

# Convert ECEF coordinates to spherical coordinates
def ecef_to_spherical(x, y, z):
    lon, lat, alt = pyproj.transform(ecef, geod, x, y, z, radians=True)
    return lon, lat, alt

# Convert ECEF coordinates to geodetic coordinates
def ecef_to_geodetic(x, y, z):
    lon, lat, alt = pyproj.transform(ecef, geod, x, y, z)
    return lon, lat, alt
    
# Convert from spherical to geodetic coordinates
def spherical_to_geodetic(lat, lon, alt):
    x, y, z = geod.fwd(lon, lat, alt, radians=False)
    return x, y, z

# Convert from geodetic to spherical coordinates
def geodetic_to_spherical(x, y, z):
    lon, lat, alt = geod.inv(x, y, z, radians=False)
    return lat, lon, alt

