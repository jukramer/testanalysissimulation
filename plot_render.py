import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from Test_file import cmap_dust, sdf_creator, subplot_gas, subplot_dust1, subplot_dust2, plot_sinks

n_rows = 5
n_cols = 3
fig, ax  = plt.subplots(nrows= n_rows, ncols= n_cols)
plt.style.use('dark_background')
mappable = None

# for gas distribution
cmap = cmap_dust
norm = LogNorm()
encounter = ['prograde','retrograde','incl_30']
for i in range(n_rows):
    for j in range(n_cols):
        ax = ax[i, j]
        if i < 10:
            sdf, sdf_sinks = sdf_creator(f'{encounter[j]}_0000{i}')
            mappable = subplot_gas(sdf, True)
        else:
            sdf, sdf_sinks = sdf_creator(f'{encounter[j]}_000{i}')
            mappable = subplot_gas(sdf, True)

        ax.set_xticks([])
        ax.set_yticks([])

cbar = fig.colorbar(mappable=mappable, ax=ax, location='right', fraction = 0.02, pad = 0.02)
cbar.set_label("log(rho)")
plt.tight_layout()
plt.show()








