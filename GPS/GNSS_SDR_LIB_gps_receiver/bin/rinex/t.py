from datetime import datetime, timedelta

def calculate_gps_seconds(gps_time_str):
    # Convert the given GPS time to a datetime object (truncate microseconds)
    gps_time_str = gps_time_str[:26]
    gps_time = datetime.strptime(gps_time_str, "%Y-%m-%d %H:%M:%S.%f")

    # Define the GPS epoch (start time)
    gps_epoch = datetime(1980, 1, 6, 0, 0, 0)

    # Calculate the total time difference
    time_difference = gps_time - gps_epoch

    # Total seconds since the GPS epoch
    total_seconds = time_difference.total_seconds()

    # Calculate the number of weeks since the GPS epoch
    weeks_since_epoch = total_seconds // (7 * 24 * 3600)
    
    # GPS week number with rollover consideration
    week_number = int(weeks_since_epoch % 1024)

    # Adjust for GPS rollover
    gps_rollover_epoch = gps_epoch + timedelta(weeks=week_number * 1024)
    
    # Calculate the seconds from the current rollover epoch
    seconds_from_gps_start = (gps_time - gps_rollover_epoch).total_seconds()

    return seconds_from_gps_start, week_number

# Given time in GPS format
gps_time_str = "2022-01-01 00:01:06.0688020"

# Calculate the number of seconds and GPS week number
seconds_from_gps_start, week_number = calculate_gps_seconds(gps_time_str)

# Print the results
print(f"Number of seconds from the last GPS rollover: {seconds_from_gps_start}")
print(f"GPS week number (with rollover): {week_number}")

