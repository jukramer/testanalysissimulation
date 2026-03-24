import numpy as np
import pandas as pd
import sarracen
import matplotlib.pyplot as plt

MASS_GAS = 4e-8
MASS_DUST_1 = 2e-9
MASS_DUST_2 = 2e-9


def loadData(filepath):
    sdfGas, sdfDust1, sdfDust2, sdf_sinks = sarracen.read_phantom(filepath, separate_types='all')
    
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
    sdf['x'] = sdf['x'] - sdf_sinks.at[0, 'x']
    sdf['y'] = sdf['y'] - sdf_sinks.at[0, 'y']

    sdf_sinks.at[1, 'x'] = sdf_sinks.at[1, 'x'] - sdf_sinks.at[0, 'x'] 
    sdf_sinks.at[1, 'y'] = sdf_sinks.at[1, 'y'] - sdf_sinks.at[0, 'y'] 

    sdf_sinks.at[0, 'x'] = sdf_sinks.at[0, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[0, 'y'] = sdf_sinks.at[0, 'y'] - sdf_sinks.at[0, 'y'] 
    
    # Add r distance column
    dfxVals = sdf['x'].to_numpy()
    dfyVals = sdf['y'].to_numpy()
    rVals = np.sqrt(dfxVals**2 + dfyVals**2)
    sdf['r'] = rVals
    
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
        
    
if __name__ == '__main__':
    # sdfGas, sdfDust1, sdfDust2, sdfSinks = sarracen.read_phantom('prograde/prograde_00010')
    # print(set(sdf['mass'].to_list()))
    
    sdfGas, sdfDust1, sdfDust2, sdfSinks = loadData('prograde/prograde_00010')
    # print(sdfGas)
    # print(sdfDust1)
    
    rVals, sigmaVals = calcSigma(sdfDust1, 50, 10, 150)
    plt.plot(rVals, sigmaVals)
    plt.title('Radial Binning Analysis')
    plt.xlabel ('Radius [AU]')
    plt.ylabel ('Surface density [kg/m^2]')
    plt.show()