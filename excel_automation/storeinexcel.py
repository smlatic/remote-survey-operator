############### FINAL ####################

import pandas as pd
from openpyxl import load_workbook
from collections import defaultdict
import os

filename = input("Enter the name of the text file: ")
append_data = input("Do you want to append to an existing file? (yes/no): ")

output_filename = "output.xlsx"  # default output filename

# check if we are appending to an existing excel file
append_to_existing = False
if append_data.lower() == 'yes':
    output_filename = input("Enter the name of the Excel file to append to: ")
    append_to_existing = True

# read the text file into a pandas DataFrame
with open(filename, 'r') as f:
    lines = f.readlines()

lines = [line.strip() for line in lines if line.strip() != '']

if append_to_existing:
    wb = load_workbook(output_filename)  # load existing workbook
else:
    # initialize a new workbook
    wb = Workbook()
    wb.remove(wb.active)  # remove default sheet

data_dict = defaultdict(lambda: defaultdict(list))

# parse lines
for line in lines:
    if ',' in line:  # this line contains data
        name, layer = line.split(',')
        borehole_num = '_'.join(name.split('_')[:2])  # derive borehole number
        data_dict[layer][borehole_num].append(name)

# creating sheets and writing data
for sheet_name, data in data_dict.items():
    if sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
    else:
        ws = wb.create_sheet(sheet_name)
    
    # add five empty rows for spacing
    for _ in range(5):
        ws.append([])
    
    # get the maximum length of the column data
    max_length = max(len(col) for col in data.values())
    
    # calculate total lines
    total_lines = sum(len(col) for col in data.values())
    
    # add headers
    ws.append([f"{sheet_name} Borehole", "total lines", str(total_lines), "Completed", "0", "Remaining", str(total_lines)])
    
    # add data to the worksheet
    for i in range(max_length+1):
        row = []
        for borehole_num in sorted(data.keys()):
            if i == 0:
                row.append(borehole_num)  # add header
                row.append(None)  # add blank column for spacing
            else:
                if i <= len(data[borehole_num]):
                    row.append(data[borehole_num][i-1])
                    row.append(None)  # add blank column for spacing
                else:
                    row.append("")
                    row.append(None)  # add blank column for spacing
        ws.append(row)
    
    # add footer
    for borehole_num in sorted(data.keys()):
        ws.append([borehole_num + " Num lines", len(data[borehole_num]), "0", "", "", "", ""])

# handling output filename for new files
output_file_extension = ".xlsx"
output_counter = 1

while not append_to_existing and os.path.exists(output_filename):
    output_filename = f"output{output_counter}{output_file_extension}"
    output_counter += 1

# save the workbook
wb.save(output_filename)
