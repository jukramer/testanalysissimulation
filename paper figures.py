import numpy as np
import pandas as pd
import sarracen
import matplotlib.pyplot as plt
import os
from render import render



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

sdf, sdf_sinks = sarracen.read_phantom('prograde/prograde_00000')
sdf = processData(sdf, sdf_sinks)
# print(sdf)



FOLDERS = ['prograde', 'incl_30', 'retrograde']

# #Check amount of files (timestamps)
for folder in FOLDERS:
    r_list = []
    x_list = []

    for file in os.listdir(folder):
        if file.startswith(f"{folder}_"):
            print(f"Processing {file} from {folder}")
            x_list.append(round(int(file[-3:])*0.05, 3))
        x_list.sort()
        sdf, sdf_sinks = sarracen.read_phantom(f'{folder}/{file}')
        sdf = processData(sdf, sdf_sinks)
        radius = characteristic_radius(sdf.get("r").to_numpy(), sdf.get("mass").to_numpy())
        r_list.append(radius)
        print(radius)
