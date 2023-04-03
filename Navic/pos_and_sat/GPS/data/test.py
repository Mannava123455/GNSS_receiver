import datetime

def read_rinex_header(file):
    header = {}
    with open(file, 'r') as f:
        for line in f:
            if line.startswith('END OF HEADER'):
                break
            label = line[60:].strip()
            if label != '':
                header[label] = line[:60].strip()
    return header

def read_rinex_obs(file):
    obs = []
    with open(file, 'r') as f:
        for line in f:
            if line.startswith('>'):
                break
        for line in f:
            if line.startswith('>'):
                obs.append({})
            else:
                sat_id = line[:3]
                prn = int(sat_id[1:])
                obs[-1][prn] = float(line[4:20])
    return obs

def offset_from_system_time(file):
    header = read_rinex_header(file)
    obs = read_rinex_obs(file)
    first_obs_time = datetime.datetime.strptime(header['TIME OF FIRST OBS'], '%Y %m %d %H %M %S.%f')
    system_time = datetime.datetime.utcnow()
    receiver_time = first_obs_time + datetime.timedelta(seconds=obs[0][1] / 1000)
    offset = (receiver_time - system_time).total_seconds()
    return offset

o=offset_from_system_time("gps.rnx")
