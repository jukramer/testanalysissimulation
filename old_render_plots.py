import matplotlib.pyplot as plt
import sarracen
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.colors import LogNorm
from render_functions import cmap_dust, sdf_creator, subplot_gas, subplot_dust1, subplot_dust2, plot_sinks, SECTIONAL_VIEW


n_rows = 5
n_cols = 3

fig, axes  = plt.subplots(nrows= n_rows, ncols= n_cols, figsize= (7,8))
plt.style.use('dark_background')
mappable_for_cbar = None

# for gas distribution
cmap = cmap_dust
norm = LogNorm()
encounter = ['prograde','retrograde','incl_30']
Time = [ '0 yr', '500 yr', '1000 yr', '1500 yr', '2000 yr']
for i in range(n_rows):
    for j in range(n_cols):
        ax = axes[i,j]
        if (i)< 10:
            sdf, sdf_sinks = sdf_creator(f'{encounter[j]}/{encounter[j]}_0000{i}')
        else:
            sdf, sdf_sinks = sdf_creator(f'{encounter[j]}/{encounter[j]}_000{i}')

        render = subplot_gas(sdf, sdf_sinks, True, ax, False)

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_aspect('equal')
        ax.set_xlim(-400, 400)
        ax.set_ylim(-400, 400)
        

        if i == 0:
            ax.set_title(['Prograde', 'Retrograde', 'Inclined 30°'][j], fontsize=12, pad = 10)
        
        if j == 0:
            ax.set_ylabel(Time[i], fontsize=10)

        if mappable_for_cbar is None:
            mappable_for_cbar = render
cbar = fig.colorbar(mappable= mappable_for_cbar, ax=axes, location='right', fraction = 0.08, pad = 0.01)
cbar.set_label("log(rho)")
plt.subplots_adjust(left=0.05, right=0.8, top=0.95, bottom=0.05, wspace=0.02, hspace=0.02)
plt.show()









