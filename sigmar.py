import numpy as np
import pandas as pd
import sarracen
import matplotlib.pyplot as plt


def loadData(filepath):
    sdfGas, sdfDust1, sdfDust2, sdf_sinks = sarracen.read_phantom(filepath, separate_types='all')
    sdfGas = processData(sdfGas, sdf_sinks)
    sdfDust1 = processData(sdfDust1, sdf_sinks)
    sdfDust2 = processData(sdfDust2, sdf_sinks)
    
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
    
    # Below one is not a sectional view
    dfxVals = sdf['x'].to_numpy()
    dfyVals = sdf['y'].to_numpy()
    rVals = np.sqrt(dfxVals**2 + dfyVals**2)
    sdf['r'] = rVals
    print(sdf['r'])
    
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
    
    return rVals, sigmaVals
        
    
if __name__ == '__main__':
    sdfGas, sdfDust1, sdfDust2, sdfSinks = loadData('incl_30/incl_30_00004')
    print(sdfGas)
    
    
    
    
    
    
    
    
    