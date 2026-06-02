# %%
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
plt.rcParams.update({
    "figure.figsize": (12,8),
    "font.size": 20
})
import numpy as np
import pandas as pd
import pathlib as pb
import sarracen
from scipy.interpolate import NearestNDInterpolator

MASS_GAS = 4e-8
MASS_DUST_1 = 2e-9
MASS_DUST_2 = 2e-9
GRAV_PARAM = 1.3271e11 # Solar 
RHO_SCALING = 1.988475e33 / (14959787070000)**3


def findFiles(dir, name):
    return [str(p) for p in pb.Path(dir).rglob(f'*{name}*')]


def loadData(filepath):
    global sdfSinks0
    sdfGas, sdfDust1, sdfDust2, sdf_sinks = sarracen.read_phantom(filepath, separate_types='all')
    
    sdfSinks0 = sdf_sinks.copy()
    
    sdfGas = processData(sdfGas, sdf_sinks)
    sdfDust1 = processData(sdfDust1, sdf_sinks)
    sdfDust2 = processData(sdfDust2, sdf_sinks)
    
    sdfGas['mass'] = MASS_GAS
    sdfDust1['mass'] = MASS_DUST_1
    sdfDust2['mass'] = MASS_DUST_2
    
    # Interpolations
    gaslocations = np.column_stack([sdfGas['x'], sdfGas['y'], sdfGas['z']])
    interp = NearestNDInterpolator(gaslocations, sdfGas['rho'] )
    dustlocations1 = np.column_stack([sdfDust1['x'], sdfDust1['y'], sdfDust1['z']])
    sdfDust1['rho-interp'] = interp(dustlocations1)*RHO_SCALING
    dustlocations2 = np.column_stack([sdfDust2['x'], sdfDust2['y'], sdfDust2['z']])
    sdfDust2['rho-interp'] = interp(dustlocations2)*RHO_SCALING
    
    # Dust-to-gas ratio
    sdfDust1['dust-to-gas'] = sdfDust1['rho'].to_numpy()*RHO_SCALING/sdfDust1['rho-interp'].to_numpy()
    sdfDust2['dust-to-gas'] = sdfDust2['rho'].to_numpy()*RHO_SCALING/sdfDust2['rho-interp'].to_numpy()
    
    return sdfGas, sdfDust1, sdfDust2, sdf_sinks


def processData(sdf, sdf_sinks):
    sdf.calc_density()
    
    # Centering
    # Position
    sdf['x'] = sdf['x'] - sdfSinks0.at[0, 'x']
    sdf['y'] = sdf['y'] - sdfSinks0.at[0, 'y']
    sdf['z'] = sdf['z'] - sdfSinks0.at[0, 'z']
    
    sdf_sinks.at[1, 'x'] = sdf_sinks.at[1, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[1, 'y'] = sdf_sinks.at[1, 'y'] - sdf_sinks.at[0, 'y']
    sdf_sinks.at[1, 'z'] = sdf_sinks.at[1, 'z'] - sdf_sinks.at[0, 'z']

    sdf_sinks.at[0, 'x'] = sdf_sinks.at[0, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[0, 'y'] = sdf_sinks.at[0, 'y'] - sdf_sinks.at[0, 'y']
    sdf_sinks.at[0, 'z'] = sdf_sinks.at[0, 'z'] - sdf_sinks.at[0, 'z']
    
    try:
        sdf['vx'] = sdf['vx'] - sdfSinks0.at[0, 'vx']
        sdf['vy'] = sdf['vy'] - sdfSinks0.at[0, 'vy']
        sdf['vz'] = sdf['vz'] - sdfSinks0.at[0, 'vz']

        sdf_sinks.at[1, 'vx'] = sdf_sinks.at[1, 'vx'] - sdf_sinks.at[0, 'vx']
        sdf_sinks.at[1, 'vy'] = sdf_sinks.at[1, 'vy'] - sdf_sinks.at[0, 'vy']
        sdf_sinks.at[1, 'vz'] = sdf_sinks.at[1, 'vz'] - sdf_sinks.at[0, 'vz']

        sdf_sinks.at[0, 'vx'] = sdf_sinks.at[0, 'vx'] - sdf_sinks.at[0, 'vx']
        sdf_sinks.at[0, 'vy'] = sdf_sinks.at[0, 'vy'] - sdf_sinks.at[0, 'vy']
        sdf_sinks.at[0, 'vz'] = sdf_sinks.at[0, 'vz'] - sdf_sinks.at[0, 'vz']
        
        sdf['v'] = np.sqrt(sdf['vx'].to_numpy()**2 + sdf['vy'].to_numpy()**2 + sdf['vz'].to_numpy()**2)
        
    except:
        pass
        
    # Add polar coord columns
    dfxVals = sdf['x'].to_numpy()
    dfyVals = sdf['y'].to_numpy()
    rVals = np.sqrt(dfxVals**2 + dfyVals**2)
    sdf['r'] = rVals
    
    thetaVals = np.arctan2(dfxVals, dfyVals)
    sdf['theta'] = thetaVals
    
    return sdf


def dropPart(sdf):
    partIDs = []
    sdf['r-km'] = sdf['r']*1.496e8
    sdf['v-kms'] = sdf['v']*1.496e8/(2*np.pi*3600*24*365)
    sdf['E'] = -GRAV_PARAM/sdf['r-km'] + 0.5*sdf['v-kms']**2
   
    return sdf['E']

       
def azimuthBin(sdf, col, nBins):
    azimuthBins = np.linspace(-np.pi, np.pi, nBins + 1, True)
    partIDs = []
    
    try:
        for i in range(nBins+1):
            sdfFilt = sdf[sdf['theta'].between(azimuthBins[i], azimuthBins[i+1])]
            partIDs.append(sdfFilt.index[sdfFilt[col] == sdfFilt[col].max(skipna=True)].tolist()[0])
            
    except IndexError:
        pass
        
    return partIDs


def trackPart(orbitType, struct, rVals, nSnapTrack, nAzimuthBins=50, avg=True):
    assert struct.lower() in {'gas', 'dust'}
    assert len(rVals) == 2 and (type(rVals) == tuple or type(rVals) == list)
    
    rMin, rMax = rVals
    
    if struct == 'gas':
        col = 'rho-interp'
    else:
        col = 'dust-to-gas'
        
    # Find files
    files = findFiles(orbitType, f'{orbitType}_')
    
    # Load corresponding sdf
    _, sdfTrack1, sdfTrack2, _ = loadData(files[nSnapTrack+1])
    sdfTrack1 = sdfTrack1[(sdfTrack1['r'] > rMin) & (sdfTrack1['r'] < rMax)]
    sdfTrack2 = sdfTrack2[(sdfTrack2['r'] > rMin) & (sdfTrack2['r'] < rMax)]
    idx1 = azimuthBin(sdfTrack1, col, nAzimuthBins)
    idx2 = azimuthBin(sdfTrack2, col, nAzimuthBins)
    # print('Idx1: ', idx1)
    # print('Idx2: ', idx2)
    # print('DustTrack1 length:', len(sdfTrack1.index))
    # print('DustTrack2 length:', len(sdfTrack2.index))
    
    # Array dims: tracked values x particle x snapshot
    dust1Array = np.zeros((1, nAzimuthBins, 21))
    dust2Array = np.zeros((1, nAzimuthBins, 21))
    # print(dust1Array.shape)
    
    for i in range(21):
        _, sdfDust1, sdfDust2, _ = loadData(f'{orbitType}/{orbitType}_000{i:02d}')
        print(f'\r{orbitType}: [{'▮'*(i)}{'-'*(20-i)} ]', end='')
        # print('Snapshot ', i+1)
        # print('Dust1 length: ', len(sdfDust1.index))
        # print('Dust2 length: ', len(sdfDust2.index))
        dust1Array[:,:,i] = sdfDust1.loc[idx1, col].to_numpy().T
        dust2Array[:,:,i] = sdfDust2.loc[idx2, col].to_numpy().T     
            
    if avg:
        # averages amongst all particles    
        return np.vstack([np.mean(dust1Array, 1, keepdims=True), np.mean(dust2Array, 1, keepdims=True)]), idx1, idx2
    else:
        return np.vstack([dust1Array, dust2Array]), idx1, idx2
# %%

def main():
    # %%
    nSnapTrack = 12
    plot = ['pro']
    struct = 'dust'
    
    # ================ Tracking
    if 'pro' in plot:
        trackArrPro1, trackArrPro2 = list(trackPart('prograde', struct, (35, np.inf), nSnapTrack)[0])
        trackArrPro1, trackArrPro2 = trackArrPro1.T, trackArrPro2.T
    if 'retro' in plot:
        trackArrRetro1, trackArrRetro2 = list(trackPart('retrograde', struct, (35, np.inf), nSnapTrack)[0])
        trackArrRetro1, trackArrRetro2 = trackArrRetro1.T, trackArrRetro2.T
    if 'incl' in plot:
        trackArrIncl1, trackArrIncl2 = list(trackPart('incl_30', struct, (35, np.inf), nSnapTrack)[0])
        trackArrIncl1, trackArrIncl2 = trackArrIncl1.T, trackArrIncl2.T
    # trackArrIncl = trackPart('incl_30', 'dust',(35, np.inf), nSnapTrack)[0][1].T
    
    # %%
    # %matplotlib qt
    # ================ Plotting
    tVals = np.linspace(0, 1, 21)[:,np.newaxis]
    ax: Axes
    if 'pro' in plot:
        fig, ax = plt.subplots()
        ax.plot(tVals, trackArrPro1, color="#6495ed", lw=2.5)
        ax.plot(tVals, trackArrPro2, color="#ff69b4", lw=2.5)
        ax.hlines(1, -np.inf, np.inf, colors='red', linestyles='dashed')
        ax.set_yscale('log')
        ax.set_xlabel('time [scaled units]')
        ax.legend(['St=10', 'St=1'])
        if struct == 'dust':
            ax.set_ylabel('dust to gas ratio [-]')
        else: 
            ax.set_ylabel('density [g/cm$^3$]')
        plt.show()
    
    if 'retro' in plot:
        fig, ax = plt.subplots()
        fig.set_size_inches((12,8))
        ax.plot(tVals, trackArrRetro1)
        ax.plot(tVals, trackArrRetro2)
        ax.set_yscale('log')
        ax.set_xlabel('time [scaled units]')
        ax.legend(['St=10', 'St=1'])
        if struct == 'dust':
            ax.set_ylabel('dust to gas ratio [-]')
        else: 
            ax.set_ylabel('density [g/cm$^3$]')
        plt.show()
        
    if 'incl' in plot:
        fig, ax = plt.subplots()
        ax.plot(tVals, trackArrIncl1)
        ax.plot(tVals, trackArrIncl2)
        ax.set_yscale('log')
        ax.set_xlabel('time [scaled units]')
        ax.legend(['St=10', 'St=1'])
        if struct == 'dust':
            ax.set_ylabel('dust to gas ratio [-]')
        else: 
            ax.set_ylabel('density [g/cm$^3$]')
        plt.show()        
# %%
if __name__ == '__main__':
    main()