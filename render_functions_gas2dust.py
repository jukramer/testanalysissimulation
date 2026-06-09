
import sarracen
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from matplotlib.colors import LogNorm
from scipy.interpolate import NearestNDInterpolator


def loadData(filepath):
    sdfGas, sdfDust1, sdfDust2, sdf_sinks = sarracen.read_phantom(
        filepath, separate_types='all'
    )

    x0 = sdf_sinks.at[0, 'x']
    y0 = sdf_sinks.at[0, 'y']

    sdfGas = sdf_processor(sdfGas, x0, y0)
    sdfDust1 = sdf_processor(sdfDust1, x0, y0)
    sdfDust2 = sdf_processor(sdfDust2, x0, y0)

    sdf_sinks['x'] = sdf_sinks['x'] - x0
    sdf_sinks['y'] = sdf_sinks['y'] - y0

    sdfDust = sarracen.SarracenDataFrame(
        pd.concat([sdfDust1, sdfDust2], ignore_index=True),
        params=sdfDust1.params.copy()
    )


    gaslocations = np.column_stack([sdfGas['x'], sdfGas['y'], sdfGas['z']])
    interp = NearestNDInterpolator(gaslocations, sdfGas['rho'])

    dustlocations = np.column_stack([sdfDust['x'], sdfDust['y'], sdfDust['z']])
    sdfDust['interpDustDensity'] = interp(dustlocations)

    sdfDust['dust-to-gas'] = (
        sdfDust['rho'].to_numpy() / sdfDust['interpDustDensity'].to_numpy()
    )


    return sdfGas, sdfDust, sdf_sinks


def sdf_processor(sdf, x0, y0):
    sdf.calc_density()

    sdf['x'] = sdf['x'] - x0
    sdf['y'] = sdf['y'] - y0

    sdf['r'] = np.sqrt(sdf['x']**2 + sdf['y']**2)
    sdf['theta'] = np.arctan2(sdf['y'], sdf['x'])

    return sdf

# def sdf_processor(sdf, sdf_sinks):
#     sdf.calc_density()

#     sdf['x'] = sdf['x'] - sdf_sinks.at[0, 'x']
#     sdf['y'] = sdf['y'] - sdf_sinks.at[0, 'y']

#     sdf_sinks.at[1, 'x'] = sdf_sinks.at[1, 'x'] - sdf_sinks.at[0, 'x']
#     sdf_sinks.at[1, 'y'] = sdf_sinks.at[1, 'y'] - sdf_sinks.at[0, 'y']

#     sdf_sinks.at[0, 'x'] = sdf_sinks.at[0, 'x'] - sdf_sinks.at[0, 'x']
#     sdf_sinks.at[0, 'y'] = sdf_sinks.at[0, 'y'] - sdf_sinks.at[0, 'y']

#     # Add polar coord columns
#     dfxVals = sdf['x'].to_numpy()
#     dfyVals = sdf['y'].to_numpy()
#     rVals = np.sqrt(dfxVals**2 + dfyVals**2)
#     sdf['r'] = rVals
    
#     thetaVals = np.arctan2(dfxVals, dfyVals)
#     sdf['theta'] = thetaVals

#     return sdf, sdf_sinks




# Creating dots for sink particles


# print(sdf)
# print(sdf_sinks)




def plot_sinks(ax, sdf_sinks):
    x_sink_0 = sdf_sinks.at[0, 'x']
    y_sink_0 = sdf_sinks.at[0, 'y']

    x_sink_1 = sdf_sinks.at[1, 'x']
    y_sink_1 = sdf_sinks.at[1, 'y']
    
    ax.scatter(x=x_sink_0, y=y_sink_0, color='skyblue', s=10)
    ax.scatter(x=x_sink_1, y=y_sink_1, color='red', s=10)


# function to truncated colour maps
def truncate_cmap(cmap_name, minval=0.0, maxval=1.0, n=512):
    cmap = plt.get_cmap(cmap_name)
    new_cmap = mcolors.LinearSegmentedColormap.from_list(
        f"trunc_{cmap_name}",
        cmap(np.linspace(minval, maxval, n)))
    new_cmap.set_under(color='black')
    return new_cmap

cmap_dust = truncate_cmap('Blues_r')


# Functions to render plots individually with axis and with colour bars
# sectional view at z = 0 , for sdf.itype, 1 = gas, 7 = dust (stokes = 10), 8 = dust (stokes = 1)




# def subplot_dust2gas(sdf, sdf_sinks, ax,cbar):
#     #cmap1 = truncate_cmap('gist_heat', 0.1, 1)
#     #cmap1.set_under('black')
#     ax = sdf.render('dust-to-gas', xlim=(- 150, 150), ylim=(-150, 150), log_scale=False, 
#                                     cmap='gist_heat', norm=LogNorm(1e-2, 1e1), ax = ax, cbar = cbar)
#     plot_sinks(ax, sdf_sinks=sdf_sinks)

#     if ax.images:
#         return ax.images[0]
#     elif ax.collections:
#         return ax.collections[0]
#     else:
#         return None

def subplot_dust2gas(sdfGas, sdfDust, sdf_sinks, ax, cbar=False):
    gas_render = sdfGas.render(
        'rho',
        xlim=(-150, 150),
        ylim=(-150, 150),
        log_scale=False,
        ax=ax,
        cbar=False
    )

    gas_img = gas_render.images[0].get_array().copy()

    ax.clear()

    print('Gas min:', np.nanmin(gas_img))
    print('Gas max:', np.nanmax(gas_img))

    dust_render = sdfDust.render(
        'rho',
        xlim=(-150, 150),
        ylim=(-150, 150),
        log_scale=False,
        ax=ax,
        cbar=False
    )

    dust_img = dust_render.images[0].get_array().copy()

    ax.clear()
    print('Dust min:', np.nanmin(dust_img))
    print('Dust max:', np.nanmax(dust_img))

    gas_floor = gas_img.max() * 1e-5

    ratio = np.full_like(gas_img, np.nan)

    mask = gas_img > gas_floor

    ratio[mask] = dust_img[mask] / gas_img[mask]

    print("Ratio min:", np.nanmin(ratio))
    print("Ratio max:", np.nanmax(ratio))

    im = ax.imshow(
        ratio,
        origin='lower',
        extent=(-150, 150, -150, 150),
        norm=LogNorm(1e-3, 1),
        cmap='gist_heat'
    )

    plot_sinks(ax, sdf_sinks)

    return im






