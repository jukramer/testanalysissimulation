import sarracen
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

# Column density scaling: M_sun/AU^2 --> g/cm^2
scaling_col = 8.89e6

plt.style.use('dark_background')


def sdf_creator(filename):
    sdf, sdf_sinks = sarracen.read_phantom(filename)

    # Calculate density
    sdf.calc_density()

    # Physical column density proxy
    sdf['sigma'] = sdf['rho'] * scaling_col

    # Prevent log10(0)
    sdf['sigma'] = np.clip(sdf['sigma'], 1e-30, None)

    # LOGGED VALUES
    sdf['log_sigma'] = np.log10(sdf['sigma'])

    # Shift coordinates to primary sink
    sdf['x'] = sdf['x'] - sdf_sinks.at[0, 'x']
    sdf['y'] = sdf['y'] - sdf_sinks.at[0, 'y']

    sdf_sinks.at[1, 'x'] = sdf_sinks.at[1, 'x'] - sdf_sinks.at[0, 'x']
    sdf_sinks.at[1, 'y'] = sdf_sinks.at[1, 'y'] - sdf_sinks.at[0, 'y']

    sdf_sinks.at[0, 'x'] = 0.0
    sdf_sinks.at[0, 'y'] = 0.0

    return sdf, sdf_sinks


# Load snapshot
sdf, sdf_sinks = sdf_creator('prograde/prograde_00010')


def plot_sinks(ax, sdf_sinks):
    ax.scatter(
        x=sdf_sinks.at[0, 'x'],
        y=sdf_sinks.at[0, 'y'],
        color='skyblue',
        s=10
    )

    ax.scatter(
        x=sdf_sinks.at[1, 'x'],
        y=sdf_sinks.at[1, 'y'],
        color='red',
        s=10
    )


def truncate_cmap(cmap_name, minval=0.0, maxval=1.0, n=512):
    cmap = plt.get_cmap(cmap_name)

    new_cmap = mcolors.LinearSegmentedColormap.from_list(
        f"trunc_{cmap_name}",
        cmap(np.linspace(minval, maxval, n))
    )

    new_cmap.set_under(color='black')

    return new_cmap


# ---------------------------------------------------------
# itype:
# 1 = gas
# 7 = dust (Stokes = 10)
# 8 = dust (Stokes = 1)
# ---------------------------------------------------------

def subplot_gas(sdf, sdf_sinks, SECTIONAL_VIEW, ax, cbar):

    kwargs = dict(
        xlim=(-400, 400),
        ylim=(-400, 400),
        cmap='gist_heat',
        ax=ax,
        cbar=cbar,
        vmin=-3,   # log10(1e-3)
        vmax=0     # log10(1e0)
    )

    if SECTIONAL_VIEW:
        kwargs['xsec'] = 0.00

    sdf[sdf.itype == 1].render(
        'log_sigma',
        **kwargs
    )

    plot_sinks(ax, sdf_sinks)

    if ax.images:
        return ax.images[0]
    elif ax.collections:
        return ax.collections[0]

    return None


def subplot_dust1(sdf, sdf_sinks, SECTIONAL_VIEW, ax, cbar):

    kwargs = dict(
        xlim=(-400, 400),
        ylim=(-400, 400),
        cmap='gist_heat',
        ax=ax,
        cbar=cbar,
        vmin=-4,   # log10(1e-4)
        vmax=0
    )

    if SECTIONAL_VIEW:
        kwargs['xsec'] = 0.00

    sdf[sdf.itype == 7].render(
        'log_sigma',
        **kwargs
    )

    plot_sinks(ax, sdf_sinks)

    if ax.images:
        return ax.images[0]
    elif ax.collections:
        return ax.collections[0]

    return None


def subplot_dust2(sdf, sdf_sinks, SECTIONAL_VIEW, ax, cbar):

    kwargs = dict(
        xlim=(-400, 400),
        ylim=(-400, 400),
        cmap='gist_heat',
        ax=ax,
        cbar=cbar,
        vmin=-4,
        vmax=0
    )

    if SECTIONAL_VIEW:
        kwargs['xsec'] = 0.00

    sdf[sdf.itype == 8].render(
        'log_sigma',
        **kwargs
    )

    plot_sinks(ax, sdf_sinks)

    if ax.images:
        return ax.images[0]
    elif ax.collections:
        return ax.collections[0]

    return None


# =========================================================
# Example usage
# =========================================================

fig, ax = plt.subplots(figsize=(8, 8))

im = subplot_gas(
    sdf,
    sdf_sinks,
    SECTIONAL_VIEW=False,
    ax=ax,
    cbar=False
)

cbar = plt.colorbar(im, ax=ax)
cbar.set_label(r'$\log_{10}(\Sigma \; [g/cm^2])$')

ax.set_xlabel('x [AU]')
ax.set_ylabel('y [AU]')
ax.set_title('Gas Surface Density')

plt.tight_layout()
plt.show()
