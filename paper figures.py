import numpy as np
import pandas as pd
import sarracen
import matplotlib.pyplot as plt
import os
from render import render

# FOLDERS = ['prograde']

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


# #Check amount of files (timestamps)
# for folder in FOLDERS:
#     for file in os.listdir(folder):
#         if file.startswith(f"{folder}_"):
#             print(f"Processing {file} from {folder}")
#             x_list.append(round(int(file[-3:])*0.05, 3))

# x_list.sort()
# print(x_list)


def characteristic_radius(radii , masses):

    sorted_indices = np.argsort(radii)
    sorted_radii = radii[sorted_indices]
    sorted_masses = masses[sorted_indices]

    total_mass = np.sum(masses)
    cumulative_mass = np.cumsum(sorted_masses)
    target_mass = 0.632 * total_mass

    idx = np.searchsorted(cumulative_mass, target_mass)

    
    if idx == 0:
        r_632 = sorted_radii[0]
    elif idx >= len(sorted_radii):
        r_632 = sorted_radii[-1]
    else:

        r1 = sorted_radii[idx-1]
        r2 = sorted_radii[idx]
        m1 = cumulative_mass[idx-1]
        m2 = cumulative_mass[idx]
        r_632 = r1 + (r2 - r1) * (target_mass - m1) / (m2 - m1)

    return r_632

sdf, sdf_sinks = sarracen.read_phantom('prograde/prograde_00010')
processData(sdf, sdf_sinks)
# print(sdf)

print(sdf.get("mass"))
print(sdf.get("r"))



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


