import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sarracen
from scipy.interpolate import NearestNDInterpolator

MASS_GAS = 4e-8
MASS_DUST_1 = 2e-9
MASS_DUST_2 = 2e-9
GRAV_PARAM = 1.2371e20 # Solar 

n = 0


def loadData(filepath):
    sdfGas, sdfDust1, sdfDust2, sdf_sinks = sarracen.read_phantom(filepath, separate_types='all')
    # print(sdfDust1.keys())
    
    global sdfSinks0
    sdfSinks0 = sdf_sinks.copy()
    
    global n
    n+=1
    # print(f'------------- {n} --------------')
    
    sdfGas = processData(sdfGas, sdf_sinks)
    sdfDust1 = processData(sdfDust1, sdf_sinks)
    sdfDust2 = processData(sdfDust2, sdf_sinks)
    
    # print(sdfGas.keys())
    # print(sdfDust1.keys())
    # print(sdfDust2.keys())
    
    sdfGas['mass'] = MASS_GAS
    sdfDust1['mass'] = MASS_DUST_1
    sdfDust2['mass'] = MASS_DUST_2
    
    # Interpolations
    gaslocations = np.column_stack([sdfGas['x'], sdfGas['y'], sdfGas['z']])
    interp = NearestNDInterpolator(gaslocations, sdfGas['rho'] )
    dustlocations1 = np.column_stack([sdfDust1['x'], sdfDust1['y'], sdfDust1['z']])
    sdfDust1['interpDustDensity'] = interp(dustlocations1)
    dustlocations2 = np.column_stack([sdfDust2['x'], sdfDust2['y'], sdfDust2['z']])
    sdfDust2['interpDustDensity'] = interp(dustlocations2)
    
    # Dust-to-gas ratio
    sdfDust1['dust-to-gas'] = sdfDust1['rho'].to_numpy()/sdfDust1['interpDustDensity'].to_numpy()
    sdfDust2['dust-to-gas'] = sdfDust2['rho'].to_numpy()/sdfDust2['interpDustDensity'].to_numpy()
    
    return sdfGas, sdfDust1, sdfDust2, sdf_sinks


def processData(sdf, sdf_sinks):
    sdf.calc_density()
    
    # Centering
    # Position
    sdf['x'] = sdf['x'] - sdfSinks0.at[0, 'x']
    sdf['y'] = sdf['y'] - sdfSinks0.at[0, 'y']

    sdf_sinks.at[1, 'x'] = sdf_sinks.at[1, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[1, 'y'] = sdf_sinks.at[1, 'y'] - sdf_sinks.at[0, 'y']

    sdf_sinks.at[0, 'x'] = sdf_sinks.at[0, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[0, 'y'] = sdf_sinks.at[0, 'y'] - sdf_sinks.at[0, 'y']
    
    # Velocity TODO: No velocity data on all snapshots yet
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
        
        # print('True')
    except:
        # print('false')
        pass
        
    # Add polar coord columns
    dfxVals = sdf['x'].to_numpy()
    dfyVals = sdf['y'].to_numpy()
    rVals = np.sqrt(dfxVals**2 + dfyVals**2)
    sdf['r'] = rVals
    
    thetaVals = np.arctan2(dfxVals, dfyVals)
    sdf['theta'] = thetaVals
    
    # Remove escaped particles
    # idxVals = []
    # EPotVals = -GRAV_PARAM/sdf['r'].to_numpy()
    # EKinVals = sdf['v'].to_numpy()**2/2
    # ETotVals = EPotVals + EKinVals
    # print(ETotVals[np.where(ETotVals < 0)].shape)
    
    # EKinVals = sdf[]
    
    return sdf


def calcSigma(sdf, n, rIn, rOut):
    rVals = np.linspace(rIn, rOut, n).tolist()
    sigmaVals = []
    area = []
    try:
        for i, r in enumerate(rVals):
            sdfFilt = sdf[sdf['r'].between(r, rVals[i+1])]
            m = np.sum(sdfFilt['mass'].to_numpy())
            A = np.pi*(rVals[i+1]**2 - r**2)
            sigmaVals.append(m/A)
            area.append(A)
    except IndexError:
        pass
    
    return rVals[:-1], sigmaVals, area

       
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


def trackPart(orbitType, cols, dustType, nSnapshots=13, nAzimuthBins=50, avg=True):
    assert dustType in {1,2}
    sdfGas, sdfDust1, sdfDust2, sdfSinks = loadData(f'{orbitType}/{orbitType}_00000')
    if dustType == 1:
        sdfDust = sdfDust1
    else:
        sdfDust = sdfDust2
    
    # Array dims: tracked values x particle x snapshot
    gasArray = np.zeros((len(cols), nAzimuthBins, nSnapshots))
    dustArray = np.zeros((len(cols), nAzimuthBins, nSnapshots))
    
    idxs = azimuthBin(sdfDust, 'theta', 50)
    
    for i in range(1, nSnapshots):
        try:
            sdfGas, sdfDust1, sdfDust2, sdfSinks = loadData(f'{orbitType}/{orbitType}_000{i:02d}')
            if dustType == 1:
                sdfDust = sdfDust1
            elif dustType == 2:
                sdfDust = sdfDust2
                
            dustArray[:,:,i] = sdfDust.loc[idxs, cols].to_numpy().T
            
        except FileNotFoundError:
            dustArray = np.delete(dustArray, i, 2)
            
    if avg:
        # averages amonst all particles
        return np.mean(dustArray, 1, keepdims=True)
    else:
        return dustArray


if __name__ == '__main__':
    nSnaps = 21
    meanValsArr = trackPart('retrograde', ['dust-to-gas'], 1, nSnapshots=nSnaps)
    
        
    ### PLOTTING ###
    tVals = np.linspace(0, 1, nSnaps)[:,np.newaxis]
    plt.plot(tVals, meanValsArr[0,:,:].T)
    plt.yscale('log')
    plt.show()