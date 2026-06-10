import math
import sys
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from render_functions import sdf_creator, subplot_dust1, subplot_dust2, subplot_gas
from tracking_plot_config import (
    PLOT_SPECS,
    SECTIONAL_VIEW,
    TRACKING_DATA_FILE,
    encounter,
    encounter_names,
    n_cols,
    n_rows,
    row_names,
    snapshot_filepath,
    tracking_key,
    zoom_limits,
)

NORM_LIMITS = {
    'gas': {
        'prograde': (3.6e-11, 1e-6),
        'retrograde': (3.6e-11, 1e-6),
        'incl_30': (3.6e-11, 1e-6),
    },
    'dust1': {
        'prograde': (1e-11, 1e-6),
        'retrograde': (1e-11, 1e-6),
        'incl_30': (1e-11, 1e-6),
    },
    'dust2': {
        'prograde': (1e-11, 1e-6),
        'retrograde': (1e-11, 1e-6),
        'incl_30': (1e-11, 1e-6),
    },
}

ROW_STRUCT_MAP = ['gas', 'dust1', 'dust2']


def load_tracking_data(cache_filename=TRACKING_DATA_FILE):
    try:
        with np.load(cache_filename) as data:
            return {key: data[key] for key in data.files}
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f'Missing {cache_filename}. Run save_tracking_data.py first.'
        ) from exc


def make_tracking_plot(snapshot, time_label, output_filename, tracking_data):
    fig = plt.figure(figsize=(11, 10), facecolor='white')

    gs = GridSpec(
        n_rows, n_cols + 1,
        figure=fig,
        width_ratios=[1] * n_cols + [0.05],
        wspace=0.02,
        hspace=0.05,
    )

    axes = np.empty((n_rows, n_cols), dtype=object)
    for i in range(n_rows):
        for j in range(n_cols):
            axes[i, j] = fig.add_subplot(gs[i, j])

    cax = fig.add_subplot(gs[:, -1])
    mappable_for_cbar = None
    cbar_vmin = cbar_vmax = None

    n_enc = len(encounter)
    for j, enc in enumerate(encounter):
        print(f'  [{j+1}/{n_enc}] Loading {enc}...', end=' ', flush=True)
        filepath = snapshot_filepath(enc, snapshot)

        x1 = tracking_data[tracking_key(snapshot, enc, 'x1')]
        y1 = tracking_data[tracking_key(snapshot, enc, 'y1')]
        x2 = tracking_data[tracking_key(snapshot, enc, 'x2')]
        y2 = tracking_data[tracking_key(snapshot, enc, 'y2')]

        mask1 = ~np.isnan(x1) & ~np.isnan(y1)
        mask2 = ~np.isnan(x2) & ~np.isnan(y2)
        sdf, sdf_sinks = sdf_creator(filepath)

        row_funcs = [subplot_gas, subplot_dust1, subplot_dust2]
        scatter_specs = [
            [(x1, y1, mask1, 'cyan', '$St = 10$'), (x2, y2, mask2, 'lime', '$St = 1$')],
            [(x1, y1, mask1, 'cyan', '$St = 10$')],
            [(x2, y2, mask2, 'lime', '$St = 1$')],
        ]

        for i in range(n_rows):
            print(f'panel [{i+1}/{n_rows}]', end=' ', flush=True)
            ax = axes[i, j]
            struct_key = ROW_STRUCT_MAP[i]
            vmin, vmax = NORM_LIMITS[struct_key][enc]

            render = row_funcs[i](sdf, sdf_sinks, SECTIONAL_VIEW, ax, False, vmin=vmin, vmax=vmax)

            if render is not None:
                render.set_clim(vmin, vmax)

            for sx, sy, smask, sc, slab in scatter_specs[i]:
                ax.scatter(
                    sx[smask], sy[smask],
                    s=8, c=sc, marker='o', alpha=0.85,
                    linewidths=0, zorder=5, label=slab,
                )

            xmin, xmax, ymin, ymax = zoom_limits[i][enc]
            ax.set_xlim(xmin, xmax)
            ax.set_ylim(ymin, ymax)
            ax.set_aspect('equal', adjustable='box')

            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlabel('')
            ax.set_ylabel('')

            if i == 0:
                ax.set_title(encounter_names[j], fontsize=12, color='black')

            if j == 0:
                ax.text(
                    -0.26,
                    0.5,
                    row_names[i],
                    transform=ax.transAxes,
                    rotation=90,
                    va='center',
                    ha='center',
                    fontsize=12,
                    color='black',
                )

            scale = int(xmax - xmin)
            ax.text(
                xmin + 0.10 * (xmax - xmin),
                ymin + 0.10 * (ymax - ymin),
                f'{scale} AU',
                color='white',
                fontsize=8,
            )

            if j == 0:
                ax.legend(
                    loc='upper right',
                    fontsize=7,
                    framealpha=0.5,
                    markerscale=1.5,
                    labelcolor='white',
                    facecolor='#111111',
                    edgecolor='none',
                    bbox_to_anchor=(0.98, 0.98),
                )

            if mappable_for_cbar is None and render is not None:
                mappable_for_cbar = render
                cbar_vmin, cbar_vmax = vmin, vmax

        print(f'[{j+1}/{n_enc}] {enc} done', flush=True)

    if mappable_for_cbar is not None:
        log_vmin = math.ceil(math.log10(cbar_vmin))
        log_vmax = math.floor(math.log10(cbar_vmax))
        tick_vals = [10**i for i in range(log_vmin, log_vmax + 1)]
        tick_labels = [f'$10^{{{i}}}$' for i in range(log_vmin, log_vmax + 1)]
        cbar = fig.colorbar(mappable_for_cbar, cax=cax)
        cbar.set_ticks(tick_vals)
        cbar.set_ticklabels(tick_labels)
        cbar.outline.set_edgecolor('black')
        cbar.outline.set_linewidth(1.5)
        cbar.ax.yaxis.label.set_color('black')
        cbar.ax.tick_params(colors='black', labelsize=10)
        cbar.solids.set_alpha(0.85)
        cbar.set_label(r"Log Column Density [$M_\odot$/AU$^2$]", fontsize=12)

    print('  Saving...', end=' ', flush=True)
    fig.suptitle(
        f'Tracked Dust Particles on Gas and Dust Structures at t = {time_label}',
        fontsize=16,
        color='black',
        y=0.98,
    )

    fig.subplots_adjust(top=0.92)

    plt.savefig(
        output_filename,
        dpi=300,
        bbox_inches='tight',
        facecolor='white',
    )

    plt.close(fig)
    print('done', flush=True)


if __name__ == '__main__':
    tracking_data = load_tracking_data()
    n_specs = len(PLOT_SPECS)
    for idx, spec in enumerate(PLOT_SPECS):
        print(f'[{idx+1}/{n_specs}] Snapshot {spec["snapshot"]} (t={spec["time_label"]})')
        make_tracking_plot(
            snapshot=spec['snapshot'],
            time_label=spec['time_label'],
            output_filename=spec['output_filename'],
            tracking_data=tracking_data,
        )
        print(f'[{idx+1}/{n_specs}] Snapshot {spec["snapshot"]} finished')
        sys.stdout.flush()
