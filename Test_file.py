import pandas as pd
import sarracen
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.colors import LogNorm



SECTIONAL_VIEW = True

sdf, sdf_sinks = sarracen.read_phantom('prograde/prograde_00010')


sdf.calc_density()

# sdf.describe()
print(sdf)
print(sdf_sinks)
# print(sdf['itype'].value_counts())


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

print(sdf)
print(sdf_sinks)

plt.style.use('dark_background')

# Below one is not a sectional view

# ax = sdf[sdf.itype == 1].render('rho', xlim=(x_sink_0 - 700, x_sink_0 + 700), ylim=(y_sink_0 - 700, y_sink_0 + 700), log_scale=True, xsec=0.00)
# ax = sdf[sdf.itype == 1].render('rho', xlim=(x_sink_0 - 700, x_sink_0 + 700), ylim=(y_sink_0 - 700, y_sink_0 + 700), log_scale=True)

# Sink particles visualisation

def plot_sinks(ax):
    ax.scatter(x=x_sink_0, y=y_sink_0, color='white')
    ax.scatter(x=x_sink_1, y=y_sink_1, color='white')


# function to truncated colour maps
def truncate_cmap(cmap_name, minval=0.0, maxval=1.0, n=512):
    cmap = plt.get_cmap(cmap_name)
    new_cmap = mcolors.LinearSegmentedColormap.from_list(
        f"trunc_{cmap_name}",
        cmap(np.linspace(minval, maxval, n)))
    new_cmap.set_under(color='black')
    return new_cmap
cmap_dust = truncate_cmap('Blues_r')

# sectional view at z = 0 , for sdf.itype, 1 = gas, 7 = dust (stokes = 10), 8 = dust (stokes = 1)
cmap1 = truncate_cmap('gist_heat', 0.1, 1)
cmap1.set_under('black')


if SECTIONAL_VIEW:
    ax_1 = sdf[sdf.itype == 1].render('rho', xlim=(- 400, 400), ylim=(-400, 400), log_scale=True, xsec=0.00,
                                      cmap='bone')
    ax_1.set_title("Gas Distribution in Disc")
    cbar = plt.gcf().axes[-1]
    cbar.set_ylabel(r"$\log(\rho)$")
    plot_sinks(ax_1)
    plt.show()

    ax_2 = sdf[sdf.itype == 7].render('rho', xlim=(- 400, 400), ylim=(-400, 400), log_scale=False, xsec=0.00,
                                      cmap= cmap1, norm = LogNorm(1e-8, 3.6e-12))
    plot_sinks(ax_2)
    ax_2.set_title("Dust Distribution in Disc (Stokes Number = 10)")
    cbar = plt.gcf().axes[-1]
    cbar.set_ylabel(r"$\log(\rho)$")
    plt.show()

    ax_3 = sdf[sdf.itype == 8].render('rho', xlim=(- 400, 400), ylim=(-400, 400), log_scale=False, xsec=0.00, cmap = cmap1, norm = LogNorm(1e-8, 3.6e-12))
    plot_sinks(ax_3)
    ax_3.set_title("Dust Distribution in Disc (Stokes Number = 1)")
    cbar = plt.gcf().axes[-1]
    cbar.set_ylabel(r"$\log(\rho)$")
    plt.show()
else:
    ax_1 = sdf[sdf.itype == 1].render('rho', xlim=(- 400, 400), ylim=(-400, 400), log_scale=True,
                                      cmap='bone')
    ax_1.set_title("Gas Distribution in Disc")
    cbar = plt.gcf().axes[-1]
    cbar.set_ylabel(r"$\log(\rho)$")
    plot_sinks(ax_1)
    plt.show()

    ax_2 = sdf[sdf.itype == 7].render('rho', xlim=(- 400, 400), ylim=(-400, 400), log_scale=False,
                                      cmap= cmap1, norm = LogNorm(1e-8, 3.6e-12))
    plot_sinks(ax_2)
    ax_2.set_title("Dust Distribution in Disc (Stokes Number = 10)")
    cbar = plt.gcf().axes[-1]
    cbar.set_ylabel(r"$\log(\rho)$")
    plt.show()

    ax_3 = sdf[sdf.itype == 8].render('rho', xlim=(- 400, 400), ylim=(-400, 400), log_scale=False, cmap = cmap1, norm = LogNorm(1e-8, 3.6e-12))
    plot_sinks(ax_3)
    ax_3.set_title("Dust Distribution in Disc (Stokes Number = 1)")
    cbar = plt.gcf().axes[-1]
    cbar.set_ylabel(r"$\log(\rho)$")
    plt.show()









