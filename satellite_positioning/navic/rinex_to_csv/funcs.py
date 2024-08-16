import georinex as gr
import pandas as pd
import csv


def rinex_to_csv(rinex_file, output_file):
    rinex_data = gr.load(rinex_file)
    constel_data = rinex_data.to_dataframe()
    constel_data.to_csv(output_file, sep=',', index=True)


def remove_empty_rows(input_file_path, output_file_path):
    # Open the CSV file for reading
    with open(input_file_path, 'r') as input_file:
        # Create a CSV reader object
        reader = csv.reader(input_file)

        # Create a list to hold the rows with non-empty cells
        non_empty_rows = []

        # Loop over each row in the CSV file
        for row in reader:
            # Check if any cell in the row is empty
            if '' not in row:
                # If there are no empty cells, append the row to the non_empty_rows list
                non_empty_rows.append(row)

    # Open the CSV file for writing
    with open(output_file_path, 'w', newline='') as output_file:
        # Create a CSV writer object
        writer = csv.writer(output_file)

        # Write each non-empty row to the output file
        for row in non_empty_rows:
            writer.writerow(row)

