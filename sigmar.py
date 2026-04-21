import numpy as np
import pandas as pd
import sarracen
import matplotlib.pyplot as plt
from scipy.interpolate import NearestNDInterpolator

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


def processData(sdf, sdf_sinks):
    sdf.calc_density()
    
    # Centering
    sdf['x'] = sdf['x'] - sdfSinks0.at[0, 'x']
    sdf['y'] = sdf['y'] - sdfSinks0.at[0, 'y']

    sdf_sinks.at[1, 'x'] = sdf_sinks.at[1, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[1, 'y'] = sdf_sinks.at[1, 'y'] - sdf_sinks.at[0, 'y']

    sdf_sinks.at[0, 'x'] = sdf_sinks.at[0, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[0, 'y'] = sdf_sinks.at[0, 'y'] - sdf_sinks.at[0, 'y']
    
    # Add polar coord columns
    dfxVals = sdf['x'].to_numpy()
    dfyVals = sdf['y'].to_numpy()
    rVals = np.sqrt(dfxVals**2 + dfyVals**2)
    sdf['r'] = rVals
    
    thetaVals = np.arctan2(dfxVals, dfyVals)
    sdf['theta'] = thetaVals
    
    return sdf


def calcSigma(sdf, n, rIn, rOut):
    rVals = np.linspace(rIn, rOut, n).tolist()
    sigmaVals = []
    
    try:
        for i, r in enumerate(rVals):
            sdfFilt = sdf[sdf['r'].between(r, rVals[i+1])]
            m = np.sum(sdfFilt['mass'].to_numpy())
            A = np.pi*(rVals[i+1]**2 - r**2)
            sigmaVals.append(m/A)
            
    except IndexError:
        pass
    
    return rVals[:-1], sigmaVals


def azimuthBin(sdf, col, nBins):
    azimuthBins = np.linspace(-np.pi, np.pi, nBins, True)
    partIDs = []
    
    try:
        for i in range(nBins):
            sdfFilt = sdf[sdf['theta'].between(azimuthBins[i], azimuthBins[i+1])]
            partIDs.append(sdfFilt.index[sdfFilt[col] == sdfFilt[col].max(skipna=True)].tolist()[0])
            
    except IndexError:  
        pass
        
    return partIDs


def trackPart(filepath):
    sdfGas, sdfDust1, sdfDust2, sdfSinks = loadData(filepath)
    
    # Gas Density Interpolation
    gaslocations = np.column_stack([sdfGas['x'], sdfGas['y'], sdfGas['z']])
    dustlocations = np.column_stack([ sdfDust1['x'], sdfDust1['y'], sdfDust1['z']])
    interp = NearestNDInterpolator(gaslocations, sdfGas['rho'] )
    interpDustDensity = interp(dustlocations)
    

if __name__ == '__main__':
    sdfGas, sdfDust1, sdfDust2, sdfSinks = loadData('prograde/prograde_00004')

    # gas density interpolator:
    gaslocations = np.column_stack([sdfGas['x'], sdfGas['y'], sdfGas['z']])
    dust1locations = np.column_stack([ sdfDust1['x'], sdfDust1['y'], sdfDust1['z']])
    interp = NearestNDInterpolator(gaslocations, sdfGas['rho'] )
    sdfDust1['interpdustdensity'] = interp(dust1locations)
    
    # still have to merge the two sets of dust values
    print(azimuthBin(sdfDust1, 'interpdustdensity', 50))

    # Plotting 
    if False:
        rVals, sigmaVals = calcSigma(sdfDust1, 40, 10, 150)
        plt.plot(rVals, sigmaVals)
        plt.xlabel ('Radius [AU]')
        plt.ylabel ('Surface density [kg/m^2]')
        plt.yscale('log')
        plt.show()