# Test file 2.0

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

print(loadData('prograde/prograde_00005'))