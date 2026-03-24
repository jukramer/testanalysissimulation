import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from Test_file import *

n_rows = 12
n_cols = 3
fig, ax  = plt.subplots(nrows= n_rows, ncols= n_cols)

mappable = None

# for gas distribution
cmap = cmap_dust
norm = LogNorm()
for i in range(n_rows):
    for j in range(n_cols):
        if i < 10:
            ax[i,j] = subplot_gas(f'prograde_0000{i}')
        else:
            ax[i,j] = subplot_gas(f'prograde_000{i}')
        ax.set_xticks([])
        ax.set_yticks([])

cbar = fig.colorbar(mappable=mappable, ax=ax, location='right', fraction = 0.02, pad = 0.02)
cbar.set_label("log(rho)")
plt.tight_layout()
plt.show()








