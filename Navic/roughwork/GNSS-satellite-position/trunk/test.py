import os
import rtklib

# Define the paths to the input .rnx and output .18N files
rnx_file_path = 'gps.rnx'
ionex_file_path = 'gps.18N'

# Check if the input file exists
if not os.path.exists(rnx_file_path):
    print('Error: input file not found.')
    exit()

# Call the rinex2nav function from the rtklib library
options = rtklib.default_nav_options()
status = rtklib.rinex2nav(rnx_file_path, ionex_file_path, options)

# Check if the conversion was successful
if status != 0:
    print('Error: conversion failed.')
else:
    print('Conversion successful.')

