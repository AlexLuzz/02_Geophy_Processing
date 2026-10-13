
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
from scipy.interpolate import interp1d

def build_vwc_norm_cmap():
    ticks = np.arange(0, 0.6, 0.05)
    cmap = ListedColormap(plt.colormaps["jet_r"](np.linspace(0, 1, len(ticks))))
    cmap.set_under("darkred")
    cmap.set_over("navy")
    norm = BoundaryNorm(ticks, cmap.N)
    return norm, cmap, ticks

def plot_profile(ax, station_metadata, station_name, sensors=["CS616"], max_depth=None):
    layers = station_metadata[station_name]['layers']

    soil_colors = {
        "topsoil": "#8fe26e",
        "uncompacted_overburden": "#d9c6a3",
        "compacted_overburden": "#bfa68f",
        "rock_top": "#808080",
        "rock_slope": "#808080",
        "tailings": "#996969",
    }

    sensor_colors = {
        "CS616": "#ff0000",
        "5TM": "#00cc00",
        "CS229": "#0000ff",
    }

    # "layers":[[depth, soil_type], ...]
    for i, (depth, soil_type) in enumerate(layers):
        ax.axhspan(layers[i-1][0] if i else 0, depth, 
                   color=soil_colors[soil_type], alpha=0.4)
        ax.text(0, depth - 5, 
                soil_type.replace("_", " ").title(), #.title() to capitalize first letter
                ha="center", fontsize=5, color="black", alpha=0.7)

    for s in sensors:
        if s in station_metadata[station_name]:
            ax.scatter([0]*len(station_metadata[station_name][s]["depths"]), station_metadata[station_name][s]["depths"],
                       marker="*", color=sensor_colors[s], label=s)

    ax.set(ylim=(max_depth or layers[-1][0], 0), xticks=[], ylabel="Depth", title=station_name)
    if sensors:
        ax.legend()

def plot_waterfall_v1(ax, df, cmap, norm):
    cols = [c for c in df if c.startswith("VWC_")]
    depths = np.array([float(c.split("_")[1]) for c in cols])
    order = np.argsort(depths)
    depths, cols = depths[order], np.array(cols)[order]

    t = mdates.date2num(df["TIMESTAMP"])
    v = df[cols].to_numpy().T

    # Interpolate vertically between sensor depths
    d = np.arange(0, 261)
    z = np.array([np.interp(d, depths, row) for row in v.T]).T

    cf = ax.pcolormesh(t, d, z, cmap=cmap, norm=norm, shading="auto")
    ax.set(ylim=(260, 0), ylabel="Depth (cm)")
    ax.xaxis_date()
    return cf

from scipy.interpolate import griddata
import matplotlib.dates as mdates

def plot_waterfall_v2(ax, df, cmap, norm):
    cols = [c for c in df if c.startswith("VWC_")]
    t = mdates.date2num(df["TIMESTAMP"])
    d = np.array([float(c.split("_")[1]) for c in cols])

    # Time-depth grid
    T, D = np.meshgrid(np.linspace(t.min(), t.max(), 300),
                       np.linspace(0, 260, 260))

    # Interpolate measurements at their actual sensor depths
    v = df[cols].to_numpy().ravel()
    p = np.array([(ti, di) for ti in t for di in d])
    valid = np.isfinite(v)
    Z = griddata(p[valid], v[valid], (T, D), method="linear")

    cf = ax.contourf(T, D, Z, cmap=cmap, norm=norm, extend="both")
    ax.xaxis_date()
    ax.set(ylim=(260, 0), ylabel="Depth (cm)")
    return cf

