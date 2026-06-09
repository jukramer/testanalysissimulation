import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import LogFormatterExponent
from matplotlib.gridspec import GridSpec
from render_functions import sdf_creator, subplot_gas
from particle_tracking import trackPart, loadData

n_rows = 1
n_cols = 3

encounter       = ['prograde', 'retrograde', 'incl_30']
encounter_names = ['Prograde', 'Retrograde', 'Inclined 30°']
snapshot        = 12
nSnapTrack      = 12
N_PART          = 50   # max tracked particles (= nAzimuthBins)

SECTIONAL_VIEW = False
scale          = 600   # AU, for the scale label

fig = plt.figure(figsize=(10, 4), facecolor='white')

gs = GridSpec(
    n_rows, n_cols + 1,
    figure=fig,
    width_ratios=[1] * n_cols + [0.08],
    wspace=0.01,
    hspace=0.1,
)

axes = np.empty((n_rows, n_cols), dtype=object)
for j in range(n_cols):
    axes[0, j] = fig.add_subplot(gs[0, j])

cax               = fig.add_subplot(gs[0, -1])
mappable_for_cbar = None

for j, enc in enumerate(encounter):
    ax       = axes[0, j]
    filepath = f'{enc}/{enc}_000{snapshot}'

    # ── Gas background ────────────────────────────────────────────────────────
    sdf, sdf_sinks = sdf_creator(filepath)
    render = subplot_gas(sdf, sdf_sinks, SECTIONAL_VIEW=SECTIONAL_VIEW,
                         ax=ax, cbar=False)
    ax.set_xlim(-300, 300)
    ax.set_ylim(-300, 300)
    ax.set_aspect('equal', adjustable='box')

    # ── Tracked particle indices at nSnapTrack ────────────────────────────────
    # trackPart is expensive (loops all 20 snapshots) but idx1/idx2 are what
    # we need; the returned value array is discarded here.
    _, idx1, idx2 = trackPart(enc, 'dust', (50, np.inf), nSnapTrack,
                               nAzimuthBins=N_PART)

    # ── Dust positions at snapshot 12 ─────────────────────────────────────────
    # loadData re-centres positions the same way sdf_creator does, so x/y are
    # in the same frame as the gas render.
    _, sdfDust1, sdfDust2, _ = loadData(filepath)

    # Guard: only keep indices that actually exist in the loaded frame
    valid1 = [i for i in idx1[:N_PART] if i in sdfDust1.index]
    valid2 = [i for i in idx2[:N_PART] if i in sdfDust2.index]

    x1 = sdfDust1.loc[valid1, 'x'].to_numpy()
    y1 = sdfDust1.loc[valid1, 'y'].to_numpy()
    x2 = sdfDust2.loc[valid2, 'x'].to_numpy()
    y2 = sdfDust2.loc[valid2, 'y'].to_numpy()

    # render_plots_tracking.py — dust position extraction
    _, sdfDust1, sdfDust2, _ = loadData(filepath)

    x1 = sdfDust1['x'].reindex(idx1[:N_PART]).to_numpy()
    y1 = sdfDust1['y'].reindex(idx1[:N_PART]).to_numpy()
    x2 = sdfDust2['x'].reindex(idx2[:N_PART]).to_numpy()
    y2 = sdfDust2['y'].reindex(idx2[:N_PART]).to_numpy()

    # ── Overlay scatter ───────────────────────────────────────────────────────

    # Drop NaN positions before scattering (particles absent at this snapshot)
    mask1 = ~np.isnan(x1) & ~np.isnan(y1)
    mask2 = ~np.isnan(x2) & ~np.isnan(y2)

    ax.scatter(x1[mask1], y1[mask1], s=8, c='cyan', marker='o',
               alpha=0.85, linewidths=0, zorder=5, label='$St = 10$')
    ax.scatter(x2[mask2], y2[mask2], s=8, c='purple', marker='o',
               alpha=0.85, linewidths=0, zorder=5, label='$St = 1$')


    # ── Cosmetics ─────────────────────────────────────────────────────────────
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title(encounter_names[j], fontsize=12, color='black')

    # Scale bar label (leftmost panel only)
    if j == 0:
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        ax.text(xmax - 0.9 * (xmax - xmin),
                ymin + 0.1 * (ymax - ymin),
                f'{scale} AU', color='white', fontsize=8)

    # Legend on the first panel only
    if j == 0:
        ax.legend(loc='upper right', fontsize=7, framealpha=0.5,
                  markerscale=1.5, labelcolor='white', facecolor='#111111',
                  edgecolor='none', bbox_to_anchor=(0.98, 0.98))

    if mappable_for_cbar is None:
        mappable_for_cbar = render

# ── Shared colour bar ─────────────────────────────────────────────────────────
cbar = fig.colorbar(mappable_for_cbar, cax=cax)
cbar = fig.colorbar(mappable_for_cbar, cax=cax)
pos = cax.get_position()
cax.set_position([pos.x0 + 0.02, pos.y0, pos.width, pos.height])

cbar.outline.set_edgecolor('black')
cbar.outline.set_linewidth(1.5)
cbar.set_label(r"Log Column Density [$M_\odot$/AU$^2$]", fontsize=12)
cbar.ax.yaxis.label.set_color('black')
cbar.ax.tick_params(colors='black')
cbar.ax.yaxis.set_major_formatter(LogFormatterExponent())

fig.suptitle('Gas Density Distribution at t = 0.6', fontsize=16, color='black',  y=0.98)
fig.subplots_adjust(top=0.85)

plt.savefig('gas_distr_t0.6.png', dpi=300, bbox_inches='tight',
            facecolor='white')
plt.show()