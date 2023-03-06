import georinex as gr
import pandas as pd

# Load a RINEX file
rinex_file = '1.rnx'     #observation data 
#rinex_file = 'WROC00POL_R_20230610630_15M_GN.rnx'        #GPS navigation data 
rinex_data = gr.load(rinex_file)

# Extract data of the constellation    

constel_data = rinex_data.to_dataframe()

output_file = 'data.csv'
constel_data.to_csv(output_file, sep=',', index=True)


# Read the CSV file
constel_data = pd.read_csv('data.csv')

# Select data for a specific satellite
satellite_id = 'I02'
satellite_data = constel_data[constel_data['sv'] == satellite_id]
print(satellite_data)

