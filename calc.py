import numpy as np
import pandas as pd
import sarracen
import matplotlib.pyplot as plt


def loadData():
    sdf, sdf_sinks = sarracen.read_phantom('prograde/prograde_00010')

    sdf.calc_density()
    # print(sdf)
    # print(sdf_sinks)
    
    # Centering
    sdf['x'] = sdf['x'] - sdf_sinks.at[0, 'x']
    sdf['y'] = sdf['y'] - sdf_sinks.at[0, 'y']

    sdf_sinks.at[1, 'x'] = sdf_sinks.at[1, 'x'] - sdf_sinks.at[0, 'x'] 
    sdf_sinks.at[1, 'y'] = sdf_sinks.at[1, 'y'] - sdf_sinks.at[0, 'y'] 

    sdf_sinks.at[0, 'x'] = sdf_sinks.at[0, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[0, 'y'] = sdf_sinks.at[0, 'y'] - sdf_sinks.at[0, 'y'] 

    #Creating dots for sink particles
    x_sink_0 = sdf_sinks.at[0, 'x'] 
    y_sink_0 = sdf_sinks.at[0, 'y'] 

    x_sink_1 = sdf_sinks.at[1, 'x']
    y_sink_1 = sdf_sinks.at[1, 'y']


    #Separate into different itypes

    sdf_gas = sdf[sdf.itype == 1].copy()
    sdf_dust_1 = sdf[sdf.itype == 7].copy()
    sdf_dust_2 = sdf[sdf.itype == 8].copy()
    
    plt.style.use('dark_background')

    # Below one is not a sectional view
    # ax = sdf[sdf.itype == 1].render('rho', xlim=(- 400,  400), ylim=(-400, 400), log_scale=True, xsec=0.00)
    dfxVals = sdf['x'].to_numpy()
    dfyVals = sdf['y'].to_numpy()
    rVals = np.sqrt(dfxVals**2 + dfyVals**2)
    sdf['r'] = rVals
    print(sdf['r'])
    
    return sdf
    

    # Sink particles visualisation
    # ax.scatter(x=x_sink_0, y=y_sink_0, color='white')
    # ax.scatter(x=x_sink_1, y=y_sink_1, color='white')    
    
    # print(sdf)
    # print(sdf_sinks)
    
    
def sigma(sdf, n, rIn, rOut):
    rVals = np.linspace(rIn, rOut, n).tolist()
    sigVals = []
    
    try:
        for i, r in enumerate(rVals):
            sdfFilt = sdf[sdf['r'].between(r, rVals[i+1])]
            m = np.sum(sdfFilt['mass'].to_numpy())
            A = np.pi*(rVals[i+1]**2 - r**2)
            sigVals.append(m/A)
            
    except IndexError:
        pass
    
    return rVals, sigVals
        
    
if __name__ == '__main__':
    sdf = loadData()
    sdfGrouped = sdf.groupby('itype')
    sdfGas = sdfGrouped.get_group(1)
    sdfDust1 = sdfGrouped.get_group(7)
    sdfDust2 = sdfGrouped.get_group(8)
    
    rVals, sigVals = sigma(sdfGas, 100, 10, 150)
    plt.plot(rVals[:-1], sigVals)
    plt.title('Radial Binning Analysis')
    plt.xlabel ('Radius [AU]')
    plt.ylabel ('Surface density [kg/m^2]')
    plt.show()
    
    
    
    
    
    
    
    
    