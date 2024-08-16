from pyRinex import RinexObsFile

# Read and parse the observation file
obs_data = RinexObsFile(obs_file_path)

# Get the list of satellite IDs available in the observation file
satellite_ids = obs_data.get_satellite_ids()

# Iterate over the satellite IDs
for sat_id in satellite_ids:
    # Extract the signal measurements for the current satellite
    measurements = obs_data.get_measurements(sat_id)
    
    # Process the measurements as needed
    # ...

