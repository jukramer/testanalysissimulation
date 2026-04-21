import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from Test_file import cmap_dust, sdf_creator, subplot_gas, SECTIONAL_VIEW
# TODO implement render_functions instead of test_files
# TODO Clean up python files, delete irrelevant
# TODO Pick relevant times
n_rows = 5
n_cols = 3

fig = plt.figure(figsize=(8, 10))
gs = GridSpec(n_rows, 4, figure=fig, width_ratios=[1, 1, 1, 0.08], wspace=0.05, hspace=0.05)

axes = np.empty((n_rows, n_cols), dtype=object)
for i in range(n_rows):
    for j in range(n_cols):
        axes[i, j] = fig.add_subplot(gs[i, j])

cax = fig.add_subplot(gs[:, 3])

mappable_for_cbar = None
encounter = ['prograde', 'retrograde', 'incl_30']
Time = ['0 yr', '500 yr', '1000 yr', '1500 yr', '2000 yr']

for i in range(n_rows):
    for j in range(n_cols):
        ax = axes[i, j]
        if (i+6)< 10:
            sdf, sdf_sinks = sdf_creator(f'{encounter[j]}/{encounter[j]}_0000{i+6}')
        else:
            sdf, sdf_sinks = sdf_creator(f'{encounter[j]}/{encounter[j]}_000{i+6}')

        render = subplot_gas(sdf, sdf_sinks, True, ax, False)

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_aspect('equal')
        ax.set_xlim(-400, 400)
        ax.set_ylim(-400, 400)

        if i == 0:
            ax.set_title(['Prograde', 'Retrograde', 'Inclined 30°'][j], fontsize=12, pad=10)

        if j == 0:
            ax.text(-0.12, 0.5, Time[i], transform=ax.transAxes,
                    rotation=90, va='center', ha='center', fontsize=10)

        if mappable_for_cbar is None:
            mappable_for_cbar = render

cbar = fig.colorbar(mappable_for_cbar, cax=cax)
cbar.set_label("log(rho)")

plt.show()