import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
#from Tilt_profiles_functions import render
import render
from render_functions_gas2dust import *
from matplotlib.ticker import LogFormatterExponent
# TODO update renders once all snapshots ready
# TODO adjust scale
# TODO change scale to g/cm^3

# n_rows = 5
# n_cols = 3

# plt.style.use('dark_background')

# encounter = ['prograde', 'retrograde', 'incl_30']
# Time = []
# for i in range(10,21):
#     timestamp = 812*i
#     time = f'{timestamp:0d} years'
#     Time.append(time)

# mappable_for_cbar = None
# def render_plot(mappable_for_cbar):

#     fig = plt.figure(figsize=(8, 10))
#     gs = GridSpec(n_rows, 4, figure=fig, width_ratios=[1, 1, 1, 0.08], wspace=0.05, hspace=0.05)

#     axes = np.empty((n_rows, n_cols), dtype=object)
#     for i in range(n_rows):
#         for j in range(n_cols):
#             axes[i, j] = fig.add_subplot(gs[i, j])

#     cax = fig.add_subplot(gs[:, 3])

#     snapshots = [10,11,12,16,20]
#     for i in range(n_rows):
#         for j in range(n_cols):
#             ax = axes[i, j]

#             sdfGas, sdfDust, sdf_sinks = loadData(f'{encounter[j]}/{encounter[j]}_000{snapshots[i]}')
#             sdfDust = sdfDust[sdfDust['dust-to-gas'] > 1e-2]

#             #render = subplot_dust2gas(sdfDust, sdf_sinks, ax=ax, cbar=False)
#             render = subplot_dust2gas(sdfGas, sdfDust, sdf_sinks, ax=ax, cbar=False)

            

            
            
#             ax.set_xticks([])
#             ax.set_yticks([])
#             ax.set_xlabel('')
#             ax.set_ylabel('')
#             ax.set_aspect('equal')
#             ax.set_xlim(-150, 150)
#             ax.set_ylim(-150, 150)

#             if i == 0:
#                 ax.set_title(['Prograde', 'Retrograde', 'Inclined 30°'][j], fontsize=12, pad=10)

#             if j == 0:
#                 ax.text(-0.12, 0.5, Time[i], transform=ax.transAxes,
#                         rotation=90, va='center', ha='center', fontsize=10)

#             if mappable_for_cbar is None:
#                 mappable_for_cbar = render

#     cbar = fig.colorbar(mappable_for_cbar, cax=cax)
#     cbar.set_label("dust-to-gas ratio", fontsize=16)

    
#     fig.suptitle('Dust to Gas Ratio', fontsize=16, y=0.98)
#     fig.subplots_adjust(top=0.90)





# render_plot(mappable_for_cbar=None)
# plt.show()
# #plot_name_list = ['gas_distribution','dust_a_distribution','dust_b_distribution']


n_rows = 3
n_cols = 6

encounter = ['prograde', 'retrograde', 'incl_30']
Time = []
for i in [10,11,12,14,17,20]:  # only 5 rows    
    timestamp = i/20
    time = f'{timestamp}t'
    Time.append(time)

plt.style.use('dark_background')

fig = plt.figure(figsize=(14, 7), facecolor='white')
scale = 300
gs = GridSpec(
        n_rows,
        n_cols + 1,
        figure=fig,
        width_ratios=[1] * n_cols + [0.08],
        wspace=0.01,
        hspace=-0.08
    )

mappable_for_cbar = None

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
        
        sdfGas, sdfDust, sdf_sinks = loadData(f'{encounter[i]}/{encounter[i]}_000{snapshot}')
        sdfDust = sdfDust[sdfDust['dust-to-gas'] > 1e-2]

        #render = subplot_dust2gas(sdfDust, sdf_sinks, ax=ax, cbar=False)
        render = subplot_dust2gas(sdfGas, sdfDust, sdf_sinks, ax=ax, cbar=False)
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
cbar.set_label("Log Gas-to-Dust Ratio [-]", fontsize=12)
cbar.ax.yaxis.label.set_color('black')
cbar.ax.tick_params(colors='black')
cbar.ax.yaxis.set_major_formatter(LogFormatterExponent())


fig.suptitle('Dust-to-Gas Ratio', fontsize=16, y=0.98, color = 'black')
fig.subplots_adjust(top=0.90)


plt.show()
