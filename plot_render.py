import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

n_rows = 12
n_cols = 3
fig, ax  = plt.subplots(nrows= n_rows, ncols= n_cols)

mappable = None

# for gas distribution
cmap = cmap_dust
norm = LogNorm()
for i in range(n_rows):
    for j in range(n_cols):
        ax = ax[i,j]






