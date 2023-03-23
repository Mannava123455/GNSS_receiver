import pysat
from pysat.instruments.methods import orbit

# Load RINEX file
fname = 'gps.rnx'
sat_data = pysat.readers.RinexEpochReader(fname)

# Compute the satellite's orbit
orbit_info = orbit.compute_orbit(sat_data)

# Select a satellite and two adjacent epochs
sat_id = 'G01'  # change this to the desired satellite ID
epoch1 = orbit_info.index[0]
epoch2 = orbit_info.index[1]

# Compute the position vectors of the satellite at the two epochs

pos1 = orbit_info[sat_id]['position'][epoch1]
pos2 = orbit_info[sat_id]['position'][epoch2]
# Compute the time interval between the epochs (in seconds)
dt = (epoch2 - epoch1).total_seconds()

# Compute the velocity vector using the position vectors and time interval
vel = (pos2 - pos1) / dt

print('Velocity vector:', vel)

