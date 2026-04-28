import pandas as pd
import sarracen
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata


def render(filename, limits=400, itype=1):
    """
    Limits show limits of plot, itype refers to gas / dust / dust and finally sectionview enables for a column density or
    """
    
    sdf, sdf_sinks = sarracen.read_phantom(filename)
    sdf.calc_density()

    sdf['x'] = sdf['x'] - sdf_sinks.at[0, 'x']
    sdf['y'] = sdf['y'] - sdf_sinks.at[0, 'y']
    sdf['z'] = sdf['z'] - sdf_sinks.at[0, 'z']

    sdf['vx'] = sdf['vx'] - sdf_sinks.at[0, 'vx']
    sdf['vy'] = sdf['vy'] - sdf_sinks.at[0, 'vy']
    sdf['vz'] = sdf['vz'] - sdf_sinks.at[0, 'vz']


    sdf_sinks.at[1, 'x'] = sdf_sinks.at[1, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[1, 'y'] = sdf_sinks.at[1, 'y'] - sdf_sinks.at[0, 'y']
    sdf_sinks.at[1, 'z'] = sdf_sinks.at[1, 'z'] - sdf_sinks.at[0, 'z']

    sdf_sinks.at[0, 'x'] = sdf_sinks.at[0, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[0, 'y'] = sdf_sinks.at[0, 'y'] - sdf_sinks.at[0, 'y']
    sdf_sinks.at[0, 'z'] = sdf_sinks.at[0, 'z'] - sdf_sinks.at[0, 'z']



    return sdf, sdf_sinks



def calctilt(sdf, n, rIn, rOut):
    rVals = np.linspace(rIn, rOut, n).tolist()
    tiltVals = []
    sdf.insert(0, 'r', np.sqrt(sdf['x']**2 + sdf['y']**2 + sdf['z']**2))
    print(sdf)
    
    try:
        for i, r in enumerate(rVals):
            sdfFilt = sdf[sdf['r'].between(r, rVals[i+1])]
            rvec = np.array([sdfFilt['x'].to_numpy(), sdfFilt['y'].to_numpy(), sdfFilt['z'].to_numpy()])
            vvec = np.array([sdfFilt['vx'].to_numpy(), sdfFilt['vy'].to_numpy(), sdfFilt['vz'].to_numpy()])
            m = sdfFilt['mass'].to_numpy()
            Ltot = np.sum(m * np.cross(rvec, vvec, axis = 0), axis = 1)

            L_unit = Ltot / np.linalg.norm(Ltot)
            tilt = np.arccos(L_unit[2])
            tiltVals.append(tilt)
            
    except IndexError:
        pass
    
    return rVals[:-1], tiltVals


folder = 'incl_30'

radius = []
tilt = []

for file in os.listdir(folder):
    print(file)
    if file.startswith(f"{folder}_") and file[11] == '1':
        sdf, sdf_sinks = render(f"{folder}/{file}")
        rVals, tiltVals = calctilt(sdf, 30, 10, 150)
        radius.append(rVals)
        tilt.append(np.rad2deg(tiltVals))

print(radius)        
print(tilt)

time = [10,11,12,13,14,15]


#sdf, sdf_sinks = render('incl_30/incl_30_00010')
#rvals, tiltvals = calctilt(sdf, 30, 10, 150)
#plt.plot(rvals, np.rad2deg(tiltvals))
#plt.xlabel('Radius')
#plt.ylabel('Tilt (degrees)')
#plt.title('Tilt Profile')
#plt.show()


radius_arr = np.array(radius)   # shape: (n_times, n_radii)
tilt_arr = np.array(tilt)       # shape: (n_times, n_radii)
time_arr = np.array(time)       # shape: (n_times,)

R_points = radius_arr.flatten()
T_points = np.repeat(time_arr, radius_arr.shape[1])
Z_points = tilt_arr.flatten()

radius_grid = np.linspace(R_points.min(), R_points.max(), 50)
time_grid = np.linspace(T_points.min(), T_points.max(), 50)

R_grid, T_grid = np.meshgrid(radius_grid, time_grid)


# Interpolate scattered data onto the regular grid
# Methods: 'linear', 'cubic', 'nearest'
inclination_grid = griddata(
    points=(R_points, T_points),
    values=Z_points,
    xi=(R_grid, T_grid),
    method='cubic'
)

# ===================================================
# PLOT THE SURFACE
# ===================================================

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot the interpolated surface
surf = ax.plot_surface(R_grid, T_grid, inclination_grid, 
                       cmap='viridis', 
                       edgecolor='none',
                       alpha=0.9)

# Optional: overlay the original scattered points
ax.scatter(R_points, T_points, Z_points, 
           c='red', s=5, alpha=0.3, label='Original data')

# Labels
ax.set_xlabel('Radius (AU)', fontsize=12)
ax.set_ylabel('Snapshot', fontsize=12)
ax.set_zlabel('Inclination (degrees)', fontsize=12)
ax.set_title('Tilt Profile Over Time', 
             fontsize=14)

# Color bar
cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
cbar.set_label('Inclination', fontsize=10)

# Add legend
ax.legend()

plt.tight_layout()
plt.show()


