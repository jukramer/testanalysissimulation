import numpy as np
import pandas as pd
import sarracen
import matplotlib.pyplot as plt
import os
from render import render

## Setup constants
FOLDERS = ['prograde', 'incl_30', 'retrograde']
PARTICLE_INDICES = [1] # 0 = gas, 1 = dust1, 2 = dust2, 3 = sinks
COLORS = ['cornflowerblue','tab:green', 'navajowhite']

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
results3 = {}

fig_gas, ax_gas = plt.subplots()
fig_dust1, ax_dust1 = plt.subplots()
fig_dust2, ax_dust2 = plt.subplots()

for folder in FOLDERS:
    color = COLORS[FOLDERS.index(folder)]
    fs = 15
    # Gas
    results[folder] = {}
    for file in os.listdir(folder):
        x, r = 0, 0
        if file.startswith(f"{folder}_"):
            print(f"Processing {file} from {folder}")
            x = round(int(file[-3:])*0.05, 3)
            sdfGas, sdfDust1, sdfDust2, sdf_sinks = loadData(f'{folder}/{file}')
            sdf = sdfGas
            r = characteristic_radius(sdf.get('r').to_numpy(), sdf.get('mass').to_numpy())
            results[folder][x] = r
    print(results[folder])
    results[folder] = dict(sorted(results[folder].items()))
    ax_gas.plot(list(results[folder].keys()), list(results[folder].values()), linewidth = 2.5,  label=folder, color=color)

    # Dust1
    results2[folder] = {}
    for file in os.listdir(folder):
        x, r = 0, 0
        if file.startswith(f"{folder}_"):
            print(f"Processing {file} from {folder}")
            x = round(int(file[-3:])*0.05, 3)
            sdfGas, sdfDust1, sdfDust2, sdf_sinks = loadData(f'{folder}/{file}')
            sdf = sdfDust1
            r = characteristic_radius(sdf.get('r').to_numpy(), sdf.get('mass').to_numpy())
            results2[folder][x] = r
    print(results2[folder])
    results2[folder] = dict(sorted(results2[folder].items()))
    ax_dust1.plot(list(results2[folder].keys()), list(results2[folder].values()),linewidth = 2.5, label=folder, color=color)

    # Dust2
    results3[folder] = {}
    for file in os.listdir(folder):
        x, r = 0, 0
        if file.startswith(f"{folder}_"):
            print(f"Processing {file} from {folder}")
            x = round(int(file[-3:])*0.05, 3)
            sdfGas, sdfDust1, sdfDust2, sdf_sinks = loadData(f'{folder}/{file}')
            sdf = sdfDust2
            r = characteristic_radius(sdf.get('r').to_numpy(), sdf.get('mass').to_numpy())
            results3[folder][x] = r
    print(results3[folder])
    results3[folder] = dict(sorted(results3[folder].items()))
    ax_dust2.plot(list(results3[folder].keys()), list(results3[folder].values()),linewidth = 2.5 , label=folder, color=color)

ax_gas.set_xlabel("time [scaled units]", fontsize = fs)
ax_gas.set_ylabel("r63 [au]", fontsize = fs)
ax_gas.legend(fontsize = fs)
fig_gas.savefig('renders/CRGas.png')

ax_dust1.set_xlabel("time [scaled units]", fontsize = fs)
ax_dust1.set_ylabel("r63 [au]", fontsize = fs)
ax_dust1.legend(fontsize = fs)
fig_dust1.savefig('renders/CRDust1.png')

ax_dust2.set_xlabel("time [scaled units]", fontsize = fs)
ax_dust2.set_ylabel("r63 [au]", fontsize = fs)
ax_dust2.legend(fontsize = fs)
fig_dust2.savefig('renders/CRDust2.png')

plt.show()
    