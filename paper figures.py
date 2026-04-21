import numpy as np
import pandas as pd
import sarracen
import matplotlib.pyplot as plt
import os
from render import render

## Setup constants
FOLDERS = ['prograde', 'incl_30', 'retrograde']
PARTICLE_INDICES = [1] # 0 = gas, 1 = dust1, 2 = dust2, 3 = sinks
COLORS = ['tab:blue','tab:orange', 'tab:green']


def processData(sdf, sdf_sinks):
    sdf.calc_density()

    # Centering
    sdf['x'] = sdf['x'] - sdfSinks0.at[0, 'x']
    sdf['y'] = sdf['y'] - sdfSinks0.at[0, 'y']
    sdf['z'] = sdf['z'] - sdfSinks0.at[0, 'z']

    sdf_sinks.at[1, 'x'] = sdf_sinks.at[1, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[1, 'y'] = sdf_sinks.at[1, 'y'] - sdf_sinks.at[0, 'y']
    sdf_sinks.at[1, 'z'] = sdf_sinks.at[1, 'z'] - sdf_sinks.at[0, 'z']

    sdf_sinks.at[0, 'x'] = sdf_sinks.at[0, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[0, 'y'] = sdf_sinks.at[0, 'y'] - sdf_sinks.at[0, 'y']
    sdf_sinks.at[0, 'z'] = sdf_sinks.at[0, 'z'] - sdf_sinks.at[0, 'z']

    # Add r distance column
    dfxVals = sdf['x'].to_numpy()
    dfyVals = sdf['y'].to_numpy()
    dfzVals = sdf['z'].to_numpy()
    rVals = np.sqrt(dfxVals ** 2 + dfyVals ** 2 +dfzVals ** 2)
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

MASS_GAS = 4e-8
MASS_DUST_1 = 2e-9
MASS_DUST_2 = 2e-9

def loadData(filepath):
    sdfGas, sdfDust1, sdfDust2, sdf_sinks = sarracen.read_phantom(filepath, separate_types='all')

    global sdfSinks0
    sdfSinks0 = sdf_sinks.copy()

    sdfGas = processData(sdfGas, sdf_sinks)
    sdfDust1 = processData(sdfDust1, sdf_sinks)
    sdfDust2 = processData(sdfDust2, sdf_sinks)

    sdfGas['mass'] = MASS_GAS
    sdfDust1['mass'] = MASS_DUST_1
    sdfDust2['mass'] = MASS_DUST_2
    return sdfGas, sdfDust1, sdfDust2, sdf_sinks

results = {}
results2 = {}

# #Check amount of files (timestamps)
for folder in FOLDERS:
    results[folder] = {}

    for file in os.listdir(folder):
        x, r = 0, 0
        if file.startswith(f"{folder}_"):
            print(f"Processing {file} from {folder}")
            x = round(int(file[-3:])*0.05, 3)

            # sdf, sdf_sinks = sarracen.read_phantom(f'{folder}/{file}')
            sdfGas, sdfDust1, sdfDust2, sdf_sinks = loadData(f'{folder}/{file}')
            particleTypes = [sdfGas, sdfDust1, sdfDust2, sdf_sinks]

            # Get the chosen particles and concatenate to list
            chosenParticles = []
            for particleIndex in PARTICLE_INDICES:
                chosenParticles.append(particleTypes[particleIndex])
            sdf = pd.concat(chosenParticles)

            # Calculate characteristic radius and add to list
            r = characteristic_radius(sdf.get('r').to_numpy(), sdf.get('mass').to_numpy())
            results[folder][x] = r


    print(results[folder])
    results[folder] = dict(sorted(results[folder].items()))
    print(results[folder])
    plt.plot(list(results[folder].keys()), list(results[folder].values()), label=folder, color = COLORS[FOLDERS.index(folder)])

# # THIS IS FOR DASHED LINES

    results2[folder] = {}
    for file in os.listdir(folder):
        x, r = 0, 0
        if file.startswith(f"{folder}_"):
            print(f"Processing {file} from {folder}")
            x = round(int(file[-3:])*0.05, 3)

            # sdf, sdf_sinks = sarracen.read_phantom(f'{folder}/{file}')
            sdfGas, sdfDust1, sdfDust2, sdf_sinks = loadData(f'{folder}/{file}')
            particleTypes = [sdfGas, sdfDust1, sdfDust2, sdf_sinks]

            # Get the chosen particles and concatenate to list
            chosenParticles = []
            for particleIndex in PARTICLE_INDICES:
                chosenParticles.append(particleTypes[2])
            sdf = pd.concat(chosenParticles)

            # Calculate characteristic radius and add to list
            r = characteristic_radius(sdf.get('r').to_numpy(), sdf.get('mass').to_numpy())
            results2[folder][x] = r


    print(results2[folder])
    results[folder] = dict(sorted(results[folder].items()))
    print(results2[folder])
    plt.plot(list(results2[folder].keys()), list(results2[folder].values()), label=folder, linestyle='--',  color = COLORS[FOLDERS.index(folder)])



plt.xlabel("time [scaled units]")
plt.ylabel("r63,dust [au]")
plt.legend()
plt.show()
