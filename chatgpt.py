"""
SPH Simulation Visualizer
=========================
Reads binary SPH simulation files via Sarracen and produces
interactive 3D visualizations with Plotly.

Installation
------------
    pip install sarracen plotly numpy scipy pandas

Optional (for large datasets / volume rendering):
    pip install pyvista   # GPU-accelerated volume rendering

Usage
-----
    python sph_visualizer.py --file dump_00010
    python sph_visualizer.py --file dump_00010 --color vx --downsample 50000
    python sph_visualizer.py --file dump_00010 --method projection --axis z
    python sph_visualizer.py --file dump_00010 --method volume --nx 128

Adapting to other quantities
-----------------------------
Pass any column name present in your dump file to --color, e.g.:
    --color vx       (x-velocity)
    --color h        (smoothing length)
    --color u        (specific internal energy)
    --color Bx       (magnetic field x-component, if MHD)
"""

import argparse
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Sarracen for reading Phantom/GADGET SPH binaries
try:
    import sarracen
except ImportError:
    sys.exit(
        "sarracen is not installed.  Run:  pip install sarracen"
    )

# ──────────────────────────────────────────────────────────────────────────────
# 1.  DATA LOADING
# ──────────────────────────────────────────────────────────────────────────────

def load_sph_file(filepath: str) -> tuple[sarracen.SarracenDataFrame, dict]:
    """
    Load a binary SPH dump file with Sarracen.

    Sarracen auto-detects the format (Phantom HDF5, Phantom binary,
    GADGET-2 binary, …) and returns one SarracenDataFrame per particle type.

    Parameters
    ----------
    filepath : str
        Path to the dump file (no extension needed for Phantom files).

    Returns
    -------
    sdf : SarracenDataFrame
        The gas-particle dataset (largest particle type found).
    params : dict
        Global header / metadata extracted by Sarracen.
    """
    path = Path(filepath)
    if not path.exists():
        # Phantom files often have no extension – try adding common ones
        for ext in ("", ".hdf5", ".h5"):
            candidate = Path(str(filepath) + ext)
            if candidate.exists():
                path = candidate
                break
        else:
            raise FileNotFoundError(f"Cannot find SPH file: {filepath!r}")

    print(f"[load]  Reading {path} …")
    result = sarracen.read_phantom(str(path))

    # read_phantom returns a single SarracenDataFrame or a list thereof
    if isinstance(result, list):
        # Pick the type with the most particles (usually gas, type 1)
        sdf = max(result, key=len)
        print(f"[load]  Found {len(result)} particle types; "
              f"using largest ({len(sdf):,} particles).")
    else:
        sdf = result
        print(f"[load]  Loaded {len(sdf):,} particles.")

    # Extract global header parameters (time, units, etc.)
    params = dict(sdf.params) if hasattr(sdf, "params") else {}
    if "time" in params:
        print(f"[load]  Simulation time = {params['time']:.4g}")

    print(f"[load]  Available columns: {list(sdf.columns)}")
    return sdf, params


def extract_arrays(
    sdf: sarracen.SarracenDataFrame,
    color_col: str = "rho",
) -> dict:
    """
    Pull position, velocity, density, smoothing-length, and one
    user-chosen colour quantity out of the SarracenDataFrame into
    plain NumPy arrays.

    Missing columns fall back to safe defaults so the script keeps
    running even if some quantities are absent in the file.
    """
    def _col(name, default=0.0):
        if name in sdf.columns:
            return sdf[name].to_numpy(dtype=np.float32)
        warnings.warn(f"Column '{name}' not found; using default={default}.")
        return np.full(len(sdf), default, dtype=np.float32)

    data = {
        "x":   _col("x"),
        "y":   _col("y"),
        "z":   _col("z"),
        "vx":  _col("vx"),
        "vy":  _col("vy"),
        "vz":  _col("vz"),
        "rho": _col("rho", default=1.0),
        "h":   _col("h",   default=1.0),
        "m":   _col("m",   default=1.0),
    }

    # Add the user-requested colour column (may duplicate one of the above)
    if color_col not in data:
        data[color_col] = _col(color_col)

    return data


# ──────────────────────────────────────────────────────────────────────────────
# 2.  DOWNSAMPLING  (for large datasets)
# ──────────────────────────────────────────────────────────────────────────────

def downsample(data: dict, max_points: int, seed: int = 42) -> dict:
    """
    Randomly subsample all arrays to *at most* max_points entries.

    Downsampling is applied uniformly so spatial statistics are
    preserved on average. For a density-weighted sample replace
    `p` below with `data['rho'] / data['rho'].sum()`.
    """
    n = len(data["x"])
    if n <= max_points:
        return data
    rng = np.random.default_rng(seed)
    idx = rng.choice(n, size=max_points, replace=False)
    print(f"[downsample]  {n:,} → {max_points:,} particles.")
    return {k: v[idx] for k, v in data.items()}


# ──────────────────────────────────────────────────────────────────────────────
# 3.  VISUALIZATION  –  method A: 3-D scatter plot
# ──────────────────────────────────────────────────────────────────────────────

def plot_3d_scatter(
    data: dict,
    color_col: str = "rho",
    log_color: bool = True,
    opacity: float = 0.6,
    marker_size: float = 1.5,
    title: str = "SPH Particle Distribution",
) -> go.Figure:
    """
    Interactive 3-D scatter plot of SPH particles coloured by a physical
    quantity.

    Controls
    --------
    - Left-drag   : rotate
    - Right-drag  : pan
    - Scroll      : zoom
    - Double-click: reset view
    - Hover       : show particle values

    Parameters
    ----------
    log_color : bool
        Apply log10 to the colour quantity (recommended for density).
    opacity : float
        Particle marker opacity in [0, 1].  Reduce for crowded datasets.
    marker_size : float
        Marker size in pixels.  Use 1–2 for > 10⁵ particles.
    """
    c = data[color_col].copy()

    # Log-scale colouring (guard against non-positive values)
    if log_color:
        valid = c > 0
        c_plot = np.where(valid, np.log10(np.maximum(c, 1e-40)), np.nan)
        cbar_label = f"log₁₀({color_col})"
    else:
        c_plot = c
        cbar_label = color_col

    fig = go.Figure(
        go.Scatter3d(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            mode="markers",
            marker=dict(
                size=marker_size,
                color=c_plot,
                colorscale="Inferno",   # perceptually uniform, print-safe
                opacity=opacity,
                colorbar=dict(title=cbar_label),
                line=dict(width=0),     # no outline → faster rendering
            ),
            # Hover tooltip
            customdata=np.stack(
                [data["rho"], data["h"], data["vx"], data["vy"], data["vz"]],
                axis=-1,
            ),
            hovertemplate=(
                "x=%{x:.3g}  y=%{y:.3g}  z=%{z:.3g}<br>"
                "ρ=%{customdata[0]:.3g}  h=%{customdata[1]:.3g}<br>"
                "v=(%{customdata[2]:.3g}, %{customdata[3]:.3g}, "
                "%{customdata[4]:.3g})"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title="x",
            yaxis_title="y",
            zaxis_title="z",
            bgcolor="black",
            xaxis=dict(showbackground=False, color="white"),
            yaxis=dict(showbackground=False, color="white"),
            zaxis=dict(showbackground=False, color="white"),
        ),
        paper_bgcolor="black",
        font_color="white",
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# 4.  VISUALIZATION  –  method B: 2-D column-density projection
# ──────────────────────────────────────────────────────────────────────────────

def plot_projection(
    sdf: sarracen.SarracenDataFrame,
    quantity: str = "rho",
    axis: str = "z",
    nx: int = 512,
    log_scale: bool = True,
    title: str = "Column-density projection",
) -> go.Figure:
    """
    Use Sarracen's built-in SPH kernel interpolation to project a quantity
    along *axis* onto a 2-D grid, then display the result as an interactive
    heatmap.

    This method respects SPH smoothing lengths and is more physically
    accurate than a simple histogram for small particle counts.

    Parameters
    ----------
    quantity : str
        The column to project (must exist in sdf).
    axis : str
        Projection axis: 'x', 'y', or 'z'.
    nx : int
        Resolution of the output grid (nx × nx pixels).
    """
    axis = axis.lower()
    if axis not in ("x", "y", "z"):
        raise ValueError(f"axis must be 'x', 'y', or 'z'; got {axis!r}")

    # Map projection axis → the two remaining axes
    plane = {"x": ("y", "z"), "y": ("x", "z"), "z": ("x", "y")}[axis]

    print(f"[projection]  Interpolating '{quantity}' onto {nx}×{nx} grid …")

    try:
        grid = sdf.render(
            quantity,
            x=plane[0],
            y=plane[1],
            xsize=nx,
            ysize=nx,
        )
    except Exception as exc:
        print(f"[projection]  sarracen.render() failed: {exc}")
        print("[projection]  Falling back to histogram projection.")
        grid = _histogram_projection(sdf, quantity, plane, nx)

    z_plot = np.log10(np.maximum(grid, 1e-40)) if log_scale else grid
    label = f"log₁₀({quantity})" if log_scale else quantity

    fig = go.Figure(
        go.Heatmap(
            z=z_plot,
            colorscale="Inferno",
            colorbar=dict(title=label),
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title=plane[0],
        yaxis_title=plane[1],
        paper_bgcolor="black",
        font_color="white",
    )
    return fig


def _histogram_projection(
    sdf: sarracen.SarracenDataFrame,
    quantity: str,
    plane: tuple,
    nx: int,
) -> np.ndarray:
    """Fallback: mass-weighted histogram projection (no kernel smoothing)."""
    x = sdf[plane[0]].to_numpy()
    y = sdf[plane[1]].to_numpy()
    w = sdf[quantity].to_numpy() * sdf["m"].to_numpy()

    grid, _, _ = np.histogram2d(
        x, y, bins=nx, weights=w,
        range=[[x.min(), x.max()], [y.min(), y.max()]],
    )
    return grid.T


# ──────────────────────────────────────────────────────────────────────────────
# 5.  VISUALIZATION  –  method C: volume rendering via Plotly isosurfaces
# ──────────────────────────────────────────────────────────────────────────────

def plot_volume(
    data: dict,
    quantity: str = "rho",
    nx: int = 64,
    isomin_percentile: float = 50.0,
    isomax_percentile: float = 99.5,
    title: str = "Volume rendering",
) -> go.Figure:
    """
    Interpolate SPH particle data onto a regular Cartesian grid using
    a fast nearest-neighbour scheme, then render as a Plotly Volume.

    For production use consider replacing scipy NearestNDInterpolator
    with a proper SPH kernel summation (O(N·k) with a KD-tree).

    Parameters
    ----------
    nx : int
        Grid resolution per axis (nx³ voxels).  Keep ≤ 128 for speed.
    isomin_percentile / isomax_percentile : float
        Clipping percentiles for the colour / opacity range.
    """
    from scipy.interpolate import NearestNDInterpolator  # lazy import

    print(f"[volume]  Interpolating onto {nx}³ grid …")

    # Build regular grid
    axes = [np.linspace(data[k].min(), data[k].max(), nx)
            for k in ("x", "y", "z")]
    gx, gy, gz = np.meshgrid(*axes, indexing="ij")

    interp = NearestNDInterpolator(
        np.column_stack([data["x"], data["y"], data["z"]]),
        data[quantity],
    )
    gvals = interp(gx, gy, gz).astype(np.float32)

    vmin = float(np.nanpercentile(gvals, isomin_percentile))
    vmax = float(np.nanpercentile(gvals, isomax_percentile))

    fig = go.Figure(
        go.Volume(
            x=gx.ravel(),
            y=gy.ravel(),
            z=gz.ravel(),
            value=gvals.ravel(),
            isomin=vmin,
            isomax=vmax,
            opacity=0.08,          # low opacity for X-ray view
            surface_count=20,      # number of iso-surfaces
            colorscale="Inferno",
            colorbar=dict(title=quantity),
            caps=dict(x_show=False, y_show=False, z_show=False),
        )
    )
    fig.update_layout(
        title=title,
        scene=dict(bgcolor="black",
                   xaxis=dict(showbackground=False, color="white"),
                   yaxis=dict(showbackground=False, color="white"),
                   zaxis=dict(showbackground=False, color="white")),
        paper_bgcolor="black",
        font_color="white",
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# 6.  UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def print_summary(data: dict, params: dict) -> None:
    """Print a concise summary of the loaded dataset."""
    n = len(data["x"])
    print("\n── Dataset summary ──────────────────────────────────────")
    print(f"  Particles : {n:,}")
    for key in ("time", "udist", "umass", "utime"):
        if key in params:
            print(f"  {key:8s}: {params[key]}")
    extents = {k: (float(data[k].min()), float(data[k].max()))
               for k in ("x", "y", "z")}
    for ax, (lo, hi) in extents.items():
        print(f"  {ax}-range : [{lo:.4g}, {hi:.4g}]")
    print(f"  ρ range   : [{float(data['rho'].min()):.3g},"
          f" {float(data['rho'].max()):.3g}]")
    print("─────────────────────────────────────────────────────────\n")


# ──────────────────────────────────────────────────────────────────────────────
# 7.  MAIN
# ──────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Interactive 3-D SPH visualizer (Sarracen + Plotly)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--file", "-f", required=True,
        help="Path to Phantom/GADGET SPH dump file.",
    )
    p.add_argument(
        "--method", "-m",
        choices=["scatter", "projection", "volume"],
        default="scatter",
        help="Visualization method (default: scatter).",
    )
    p.add_argument(
        "--color", "-c", default="rho",
        help="Quantity used for colouring / rendering (default: rho).",
    )
    p.add_argument(
        "--downsample", "-n", type=int, default=200_000,
        help="Maximum particles to display in scatter mode (default: 200 000).",
    )
    p.add_argument(
        "--axis", "-a", default="z",
        choices=["x", "y", "z"],
        help="Projection axis for --method projection (default: z).",
    )
    p.add_argument(
        "--nx", type=int, default=512,
        help="Grid resolution for projection/volume (default: 512).",
    )
    p.add_argument(
        "--opacity", type=float, default=0.6,
        help="Marker opacity for scatter plot (default: 0.6).",
    )
    p.add_argument(
        "--marker-size", type=float, default=1.5,
        help="Marker size (px) for scatter plot (default: 1.5).",
    )
    p.add_argument(
        "--no-log", action="store_true",
        help="Disable log10 colour scaling.",
    )
    p.add_argument(
        "--output", "-o", default=None,
        help="Save figure to this HTML file instead of opening a browser.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    # ── 1. Load data ──────────────────────────────────────────────────────────
    sdf, params = load_sph_file(args.file)

    # ── 2. Extract NumPy arrays ───────────────────────────────────────────────
    data = extract_arrays(sdf, color_col=args.color)
    print_summary(data, params)

    # ── 3. Choose and run visualization ───────────────────────────────────────
    log_color = not args.no_log
    sim_time  = params.get("time", "?")
    base_title = f"SPH dump  |  t = {sim_time}"

    if args.method == "scatter":
        # Downsample for interactive scatter – Plotly handles ~200k comfortably
        plot_data = downsample(data, max_points=args.downsample)
        fig = plot_3d_scatter(
            plot_data,
            color_col=args.color,
            log_color=log_color,
            opacity=args.opacity,
            marker_size=args.marker_size,
            title=f"{base_title}  |  3-D scatter  ({args.color})",
        )

    elif args.method == "projection":
        # Full-resolution column-density map using SPH kernel interpolation
        fig = plot_projection(
            sdf,
            quantity=args.color,
            axis=args.axis,
            nx=args.nx,
            log_scale=log_color,
            title=f"{base_title}  |  {args.color} projection along {args.axis}",
        )

    elif args.method == "volume":
        # Downsample before interpolating to the volume grid
        plot_data = downsample(data, max_points=500_000)
        fig = plot_volume(
            plot_data,
            quantity=args.color,
            nx=min(args.nx, 128),   # keep volume grid manageable
            title=f"{base_title}  |  volume render  ({args.color})",
        )

    # ── 4. Output ─────────────────────────────────────────────────────────────
    if args.output:
        fig.write_html(args.output, include_plotlyjs="cdn")
        print(f"[output]  Saved interactive figure → {args.output}")
    else:
        fig.show()


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()