
input_file_path = "samples.txt"
output_file_path = "output.txt"

try:
    # Open the input file for reading
    with open(input_file_path, 'r') as input_file:
        # Read the content of the input file
        input_text = input_file.read()

    # Remove dots from the text
    modified_text = input_text.replace('.', '')

    # Open the output file for writing
    with open(output_file_path, 'w') as output_file:
        # Write the modified content to the output file
        output_file.write(modified_text)

    print("Dots removed and saved to", output_file_path)

except FileNotFoundError:
    print("Input file not found.")
except Exception as e:
    print("An error occurred:", str(e))

