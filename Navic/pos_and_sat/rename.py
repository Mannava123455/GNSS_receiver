import pandas as pd

# Read the CSV file
df = pd.read_csv('final.csv')

# Rename the column
df = df.rename(columns={'0': 'satellite position'})
df = df.rename(columns={'Unnamed: 0': 'index'})

# Write the CSV file with the new column name
df.to_csv('output.csv', index=False)

