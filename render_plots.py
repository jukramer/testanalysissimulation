import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from render_functions import sdf_creator, subplot_gas, subplot_dust1, subplot_dust2

# TODO adjust scale (keep SM/AU^3 but make sure they correspond to same equivalent scale) --> not working, something wrong with scaling or conversion?
# TODO indicate scale in renders (800UA, 300AU)

n_rows = 6
n_cols = 3


encounter = ['prograde', 'retrograde', 'incl_30']
Time = []
for i in [10,11,12,14,17,20]:  # only 5 rows
    timestamp = 812 * i
    time = f'{timestamp:d}yrs'
    Time.append(time)


def render_plot(subplot, sectional_view):
    mappable_for_cbar = None

    fig = plt.figure(figsize=(8, 12), facecolor='white')
    if subplot == 'gas':
        scale = 600
    if subplot == 'dust1':
        scale = 300
    if subplot == 'dust2':
        scale =200
    fig.text(0.05, 0.95,  f'scale: {scale}x{scale} AU', ha='left',va='top',color='black',fontsize=9)
    gs = GridSpec(n_rows, 4, figure=fig, width_ratios=[1, 1, 1, 0.08], wspace=0.02, hspace=0.01)

    axes = np.empty((n_rows, n_cols), dtype=object)
    for i in range(n_rows):
        for j in range(n_cols):
            axes[i, j] = fig.add_subplot(gs[i, j])

    cax = fig.add_subplot(gs[:, 3])

    selected_snapshots = [10,11,12,14,17,20]
    Snapshot = []
    for i in range(n_rows):
        snapshot = selected_snapshots[i]
        Snapshot.append(snapshot)
        for j in range(n_cols):
            ax = axes[i, j]
            sdf, sdf_sinks = sdf_creator(f'{encounter[j]}/{encounter[j]}_000{selected_snapshots[i]}')

            # if (i+10)< 10:
            #     sdf, sdf_sinks = sdf_creator(f'{encounter[j]}/{encounter[j]}_0000{i+6}')
            #
            # else:
            #     sdf, sdf_sinks = sdf_creator(f'{encounter[j]}/{encounter[j]}_000{i+10}')


            if subplot == 'gas':
                render = subplot_gas(sdf, sdf_sinks, SECTIONAL_VIEW = sectional_view , ax = ax, cbar = False)
                ax.set_xlim(-300, 300)
                ax.set_ylim(-300, 300)
                ax.set_aspect('equal', adjustable='box')

            if subplot == 'dust1':
                render = subplot_dust1(sdf, sdf_sinks, SECTIONAL_VIEW=sectional_view, ax=ax, cbar=False)
                ax.set_xlim(-150, 150)
                ax.set_ylim(-150, 150)
                ax.set_aspect('equal', adjustable='box')
            if subplot == 'dust2':
                render = subplot_dust2(sdf, sdf_sinks, SECTIONAL_VIEW=sectional_view, ax=ax, cbar=False)
                ax.set_xlim(-100, 100)
                ax.set_ylim(-100, 100)
                ax.set_aspect('equal', adjustable='box')

            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlabel('')
            ax.set_ylabel('')


            if i == 0:
                ax.set_title(['Prograde', 'Retrograde', 'Inclined 30°'][j], fontsize=12, pad=10,  color='black')

            if j == 0:
                ax.text(-0.05, 0.5, f'{Time[i]}, {snapshot}', transform=ax.transAxes,
                        rotation=90, va='center', ha='center', fontsize=10)

            if mappable_for_cbar is None:
                mappable_for_cbar = render

    cbar = fig.colorbar(mappable_for_cbar, cax=cax)
    cbar.set_label("log(rho)")
    cbar.ax.yaxis.label.set_color('black')
    cbar.ax.tick_params(colors='black')

    titles = {'gas': 'Gas Density Distribution',
              'dust1': 'Dust Type 1 Density Distribution (Stokes Number = 10)',
              'dust2': 'Dust Type 2 Density Distribution (Stokes Number = 1)'}
    fig.suptitle(titles[subplot], fontsize=16, y=0.98, color = 'black')
    fig.subplots_adjust(top=0.90)


SECTIONAL_VIEW = True

render_list = ['gas', 'dust1', 'dust2']

#plot_name_list = ['gas_distribution','dust_a_distribution','dust_b_distribution']
for plot in render_list:
    render_plot(plot, SECTIONAL_VIEW)
    plt.show()

