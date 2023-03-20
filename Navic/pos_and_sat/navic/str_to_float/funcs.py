import pandas as pd



def csv_to_float(input_file, output_file, columns_to_convert, num_rows_to_convert):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(input_file)
    for col in columns_to_convert:
        for i in range(num_rows_to_convert):
            try:
                df.loc[i, col] = float(df.loc[i, col])
            except ValueError:
                pass
    
    
    # Write the converted data back to a new CSV file
    df.to_csv(output_file, index=False)

