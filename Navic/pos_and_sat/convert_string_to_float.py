import pandas as pd

# Load the CSV file into a pandas DataFrame
df = pd.read_csv('data.csv')
print(df.columns)

# Specify the columns you want to convert to float
columns_to_convert = ['time', 'sv', 'SVclockBias', 'SVclockDrift', 'SVclockDriftRate', 'IODE','Crs', 'DeltaN', 'M0', 'Cuc', 'Eccentricity', 'Cus', 'sqrtA', 'Toe','Cic', 'Omega0', 'Cis', 'Io', 'Crc', 'omega', 'OmegaDot', 'IDOT','CodesL2', 'GPSWeek', 'L2Pflag', 'SVacc', 'health', 'TGD', 'IODC','TransTime']

# Specify the number of rows to convert
num_rows_to_convert = 340

for col in columns_to_convert:
    for i in range(num_rows_to_convert):
        try:
            df.loc[i, col] = float(df.loc[i, col])
        except ValueError:
            pass


# Write the converted data back to a new CSV file
df.to_csv('float.csv', index=False)
