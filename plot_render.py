import matplotlib.pyplot as plt
import sarracen
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.colors import LogNorm
from Test_file import cmap_dust, sdf_creator, subplot_gas, subplot_dust1, subplot_dust2, plot_sinks, SECTIONAL_VIEW


n_rows = 5
n_cols = 3
fig, axes  = plt.subplots(nrows= n_rows, ncols= n_cols, figsize= (7,8))
plt.style.use('dark_background')
mappable_for_cbar = None

# for gas distribution
cmap = cmap_dust
norm = LogNorm()
encounter = ['prograde','retrograde','incl_30']
for i in range(n_rows):
    for j in range(n_cols):
        ax = axes[i,j]
        if i < 10:
            sdf, sdf_sinks = sdf_creator(f'{encounter[j]}/{encounter[j]}_0000{i}')
        else:
            sdf, sdf_sinks = sdf_creator(f'{encounter[j]}/{encounter[j]}_000{i}')

        render = subplot_gas(sdf, True, ax, False)

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel('')
        ax.set_ylabel('')

        if mappable_for_cbar is None:
            mappable_for_cbar = render
cbar = fig.colorbar(mappable= mappable_for_cbar, ax=axes, location='right', fraction = 0.08, pad = 0.01)
cbar.set_label("log(rho)")
plt.subplots_adjust(right=0.8)
plt.show()

# todo fix this shit







