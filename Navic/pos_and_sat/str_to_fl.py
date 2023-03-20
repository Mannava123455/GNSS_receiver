
import pandas as pd

# Load the CSV file into a pandas DataFrame
df = pd.read_csv('updated_file.csv')
print(df.columns)

# Specify the columns you want to convert to float
columns_to_convert = ['index', 'satellite position', 'satellite velocity','satellite acceleration','time','sv']

# Specify the number of rows to convert
num_rows_to_convert = 340

for col in columns_to_convert:
    for i in range(num_rows_to_convert):
        try:
            df.loc[i, col] = float(df.loc[i, col])
        except ValueError:
            pass


# Write the converted data back to a new CSV file
df.to_csv('result_float.csv', index=False)
