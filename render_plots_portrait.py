import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import LogFormatterExponent
from matplotlib.gridspec import GridSpec
from render_functions import sdf_creator, subplot_gas, subplot_dust1, subplot_dust2


n_rows = 3
n_cols = 6

encounter = ['prograde', 'retrograde', 'incl_30']
Time = []
for i in [10,11,12,14,17,20]:  # only 5 rows
    timestamp = i/20
    time = f'{timestamp}t'
    Time.append(time)


def render_plot(subplot, sectional_view):
    mappable_for_cbar = None

    fig = plt.figure(figsize=(14, 7), facecolor='white')
    if subplot == 'gas':
        scale = 600
    if subplot == 'dust1':
        scale = 300
    if subplot == 'dust2':
        scale =300
    gs = GridSpec(
        n_rows,
        n_cols + 1,
        figure=fig,
        width_ratios=[1] * n_cols + [0.08],
        wspace=0.01,
        hspace=-0.08
    )

    axes = np.empty((n_rows, n_cols), dtype=object)

    for i in range(n_rows):
        for j in range(n_cols):
            axes[i, j] = fig.add_subplot(gs[i, j])

    cax = fig.add_subplot(gs[:, -1])

    selected_snapshots = [10, 11, 12, 14, 17, 20]

    for i in range(n_rows):  # encounters
        for j in range(n_cols):  # timestamps

            snapshot = selected_snapshots[j]

            ax = axes[i, j]

            sdf, sdf_sinks = sdf_creator(
                f'{encounter[i]}/{encounter[i]}_000{snapshot}'
            )
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
                ax.set_xlim(-150, 150)
                ax.set_ylim(-150, 150)
                ax.set_aspect('equal', adjustable='box')


            xmin, xmax = ax.get_xlim()
            ymin, ymax = ax.get_ylim()

            x_text = xmax - 0.9 * (xmax - xmin)
            y_text = ymin + 0.1 * (ymax - ymin)

            if i == 0 and j == 0:
                ax.text(x_text,y_text,f'{scale} AU',color='white',fontsize=8)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlabel('')
            ax.set_ylabel('')

            # column titles = timestamps
            if i == 0:
                ax.set_title(
                    f'{Time[j]}',
                    fontsize=12,
                    pad=10,
                    color='black'
                )

            # row labels = encounters
            if j == 0:
                ax.text(
                    -0.08,
                    0.5,
                    ['Prograde', 'Retrograde', 'Inclined 30°'][i],
                    transform=ax.transAxes,
                    rotation=90,
                    va='center',
                    ha='center',
                    fontsize=12,
                    color='black'
                )

            if mappable_for_cbar is None:
                mappable_for_cbar = render

    cbar = fig.colorbar(mappable_for_cbar, cax=cax)
    cbar.outline.set_edgecolor('black')
    cbar.outline.set_linewidth(1.5)
    cbar.set_label("Log Column Density [$M☉/AU^2$]", fontsize=12)
    cbar.ax.yaxis.label.set_color('black')
    cbar.ax.tick_params(colors='black')
    cbar.ax.yaxis.set_major_formatter(LogFormatterExponent())

    titles = {'gas': 'Gas Density Distribution',
              'dust1': 'Dust Density Distribution (St = 10)',
              'dust2': 'Dust Density Distribution (St = 1)'}
    fig.suptitle(titles[subplot], fontsize=16, y=0.98, color = 'black')
    fig.subplots_adjust(top=0.90)

SECTIONAL_VIEW = False

#render_list = ['gas','dust1','dust2']
# render_list = ['dust1','dust2']
render_list = ['gas']

#plot_name_list = ['gas_distribution','dust_a_distribution','dust_b_distribution']
for plot in render_list:
    render_plot(plot, SECTIONAL_VIEW)
    plt.savefig(
        f'{plot}_distr_draft.png',
        dpi=300,
        bbox_inches='tight',
        facecolor='white'
    )

    plt.show()

