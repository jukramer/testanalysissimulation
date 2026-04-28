import pandas as pd
import sarracen
import matplotlib.pyplot as plt
import numpy as np

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
    
    try:
        for i, r in enumerate(rVals):
            sdfFilt = sdf[sdf['r'].between(r, rVals[i+1])]
            rvec = np.array([sdfFilt['x'].to_numpy(), sdfFilt['y'].to_numpy(), sdfFilt['z'].to_numpy()])
            vvec = np.array([sdfFilt['vx'].to_numpy(), sdfFilt['vy'].to_numpy(), sdfFilt['vz'].to_numpy()])
            m = sdfFilt['mass'].to_numpy()
            Ltot = np.sum(m * np.cross(rvec, vvec, axis = 1))

            L_unit = Ltot / np.linalg.norm(Ltot)
            tilt = np.arccos(L_unit[2])
            tiltVals.append(tilt)
            
    except IndexError:
        pass
    
    return rVals[:-1], tiltVals


