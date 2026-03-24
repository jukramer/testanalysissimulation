import numpy as np
import pandas as pd
import sarracen
import matplotlib.pyplot as plt
import os
from render import render

FOLDERS = ['prograde']

x_list = []


def processData(sdf, sdf_sinks):
    sdf.calc_density()

    # Centering
    sdf['x'] = sdf['x'] - sdf_sinks.at[0, 'x']
    sdf['y'] = sdf['y'] - sdf_sinks.at[0, 'y']

    sdf_sinks.at[1, 'x'] = sdf_sinks.at[1, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[1, 'y'] = sdf_sinks.at[1, 'y'] - sdf_sinks.at[0, 'y']

    sdf_sinks.at[0, 'x'] = sdf_sinks.at[0, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[0, 'y'] = sdf_sinks.at[0, 'y'] - sdf_sinks.at[0, 'y']

    # Add r distance column
    dfxVals = sdf['x'].to_numpy()
    dfyVals = sdf['y'].to_numpy()
    rVals = np.sqrt(dfxVals ** 2 + dfyVals ** 2)
    sdf['r'] = rVals

    return sdf


#Check amount of files (timestamps)
for folder in FOLDERS:
    for file in os.listdir(folder):
        if file.startswith(f"{folder}_"):
            print(f"Processing {file} from {folder}")
            x_list.append(round(int(file[-3:])*0.05, 3))

x_list.sort()
print(x_list)


# MASS_GAS = 4e-8
# MASS_DUST_1 = 2e-9
# MASS_DUST_2 = 2e-9

# def loadData(filepath):
#     sdfGas, sdfDust1, sdfDust2, sdf_sinks = sarracen.read_phantom(filepath, separate_types='all')
    
#     sdfGas = processData(sdfGas, sdf_sinks)
#     sdfDust1 = processData(sdfDust1, sdf_sinks)
#     sdfDust2 = processData(sdfDust2, sdf_sinks)
    
#     sdfGas['mass'] = MASS_GAS
#     sdfDust1['mass'] = MASS_DUST_1
#     sdfDust2['mass'] = MASS_DUST_2
    
#     return sdfGas, sdfDust1, sdfDust2, sdf_sinks


