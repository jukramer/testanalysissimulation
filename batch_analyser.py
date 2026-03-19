import os
from render import render

OUTPUT_PATH = "Renders"
FOLDERS = ['incl_30', 'prograde', 'retrograde']

# Chek if output folders exist, make dir if non existent
if not os.path.isdir(OUTPUT_PATH):
    os.mkdir(OUTPUT_PATH)
for folder in FOLDERS:
    if not os.path.exists(f"{OUTPUT_PATH}{folder}"):
        os.mkdir(f"{OUTPUT_PATH}{folder}")


#loop through input folder, find files starting with correct filename, and output to correct location
for folder in FOLDERS:
    for file in os.listdir(folder):
        if file.startswith(f"{folder}_"):
            print(f"Processing {file} from {folder}")
            # output = render(file)
            # output.savefig(f"Renders/{folder}/{file}")


