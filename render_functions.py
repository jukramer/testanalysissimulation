
import sarracen
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.colors import LogNorm

SECTIONAL_VIEW = True

def sdf_creator(filename):
    sdf, sdf_sinks = sarracen.read_phantom(filename)
    sdf.calc_density()

    sdf['x'] = sdf['x'] - sdf_sinks.at[0, 'x']
    sdf['y'] = sdf['y'] - sdf_sinks.at[0, 'y']

    sdf_sinks.at[1, 'x'] = sdf_sinks.at[1, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[1, 'y'] = sdf_sinks.at[1, 'y'] - sdf_sinks.at[0, 'y']

    sdf_sinks.at[0, 'x'] = sdf_sinks.at[0, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[0, 'y'] = sdf_sinks.at[0, 'y'] - sdf_sinks.at[0, 'y']

    return sdf, sdf_sinks


sdf, sdf_sinks = sdf_creator('prograde/prograde_00010')

# Creating dots for sink particles


# print(sdf)
# print(sdf_sinks)

plt.style.use('dark_background')


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


def subplot_gas(sdf, sdf_sinks, SECTIONAL_VIEW, ax, cbar):
    if SECTIONAL_VIEW:
        render = sdf[sdf.itype == 1].render('rho', xlim=(- 400, 400), ylim=(-400, 400), log_scale=True, xsec=0.00,
                                            cmap='bone', ax=ax, cbar=cbar)


    else:
        render = sdf[sdf.itype == 1].render('rho', xlim=(- 400, 400), ylim=(-400, 400), log_scale=True,
                                            cmap='bone', ax=ax, cbar=cbar)
    plot_sinks(ax, sdf_sinks=sdf_sinks)

    if ax.images:
        return ax.images[0]
    elif ax.collections:
        return ax.collections[0]
    else:
        return None


def subplot_dust1(sdf, sdf_sinks, SECTIONAL_VIEW, ax,cbar):
    #cmap1 = truncate_cmap('gist_heat', 0.1, 1)
    #cmap1.set_under('black')
    if SECTIONAL_VIEW:
        ax = sdf[sdf.itype == 7].render('rho', xlim=(- 400, 400), ylim=(-400, 400), log_scale=False, xsec=0.00,
                                        cmap='bone', norm=LogNorm(3.6e-12, 1e-8), ax = ax, cbar = cbar)
        plot_sinks(ax, sdf_sinks=sdf_sinks)

    else:
        ax = sdf[sdf.itype == 7].render('rho', xlim=(- 400, 400), ylim=(-400, 400), log_scale=False,
                                        cmap='bone', norm=LogNorm(3.6e-12, 1e-8), ax = ax, cbar = cbar)
        plot_sinks(ax, sdf_sinks=sdf_sinks)

    if ax.images:
        return ax.images[0]
    elif ax.collections:
        return ax.collections[0]
    else:
        return None


def subplot_dust2(sdf, sdf_sinks, SECTIONAL_VIEW, ax, cbar):
    #cmap1 = truncate_cmap('gist_heat', 0.1, 1)
    #cmap1.set_under('black')
    if SECTIONAL_VIEW:
        ax = sdf[sdf.itype == 8].render('rho', xlim=(- 400, 400), ylim=(-400, 400), log_scale=False, xsec=0.00,
                                        cmap='bone', norm=LogNorm(3.6e-12, 1e-8), ax = ax, cbar = cbar)
        plot_sinks(ax, sdf_sinks=sdf_sinks)

    else:
        ax = sdf[sdf.itype == 8].render('rho', xlim=(- 400, 400), ylim=(-400, 400), log_scale=False, cmap='bone',
                                        norm=LogNorm(3.6e-12, 1e-8), ax = ax , cbar = cbar)
        plot_sinks(ax, sdf_sinks=sdf_sinks)

    if ax.images:
        return ax.images[0]
    elif ax.collections:
        return ax.collections[0]
    else:
        return None








