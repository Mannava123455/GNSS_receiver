def parse_rinex_file(filename):
    # Open the file and read the header
    with open(filename, 'r') as f:
        header_lines = []
        line = f.readline()
        while line.startswith((' ', '\t')):
            header_lines.append(line.strip())
            line = f.readline()
        header = '\n'.join(header_lines)

        # Parse the data section
        data_lines = []
        while line:
            data_lines.append(line.strip())
            line = f.readline()

    # Convert the data section into a list of dictionaries
    data = []
    for line in data_lines:
        sat_id = line[0:3]
        toc_year = int(line[4:6]) + 2000
        toc_month = int(line[7:9])
        toc_day = int(line[10:12])
        toc_hour = int(line[13:15])
        toc_minute = int(line[16:18])
        toc_second = float(line[19:22])
        af0 = float(line[23:42])
        af1 = float(line[42:61])
        af2 = float(line[61:80])
        data.append({
            'sat_id': sat_id,
            'toc': datetime(toc_year, toc_month, toc_day, toc_hour, toc_minute, toc_second),
            'af0': af0,
            'af1': af1,
            'af2': af2,
        })

    return header, data

# Load the RINEX file and parse the data
filename = 'example.rnx'  # replace with your file path
header, data = parse_rinex_file(filename)

# Compute the satellite clock offset
c = 299792458  # speed of light in m/s
for record in data:
    toc = record['toc']
    dt = (datetime.utcnow() - toc).total_seconds()
    clock_offset = record['af0'] + record['af1'] * dt + record['af2'] * dt**2
    sat_id = record['sat_id']
    print(f'Satellite {sat_id}: Clock offset = {clock_offset:.3e} seconds')

