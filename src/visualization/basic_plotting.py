from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.collections import LineCollection, PatchCollection
import pandas as pd
import numpy as np

def format_time_axis(ax, format='%m-%d', rotation=45):
    """Smart date locator with MM-dd format and 45-degree angle."""
    locator = mdates.AutoDateLocator(minticks=4, maxticks=12)
    formatter = mdates.DateFormatter(format)
    
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    
    # Rotate and align labels
    for label in ax.get_xticklabels():
        label.set_rotation(rotation)
        label.set_horizontalalignment('right')

def plot_sensors(df, ax, elec_numbers=None, **params):
    """Plot selected electrodes on an existing axis."""
    show_numbers = params.pop("show_numbers", False)
    number_every = params.pop("number_every", 4)

    if elec_numbers is not None:
        df = df[df["elec_number"].isin(elec_numbers)]

    scatter_kwargs = {
        "s": 10,
        "color": "darkgrey",
        "alpha": 0.8,
        **params}

    ax.scatter(df["X"], df["Z"], **scatter_kwargs)

    if show_numbers:
        for i, (_, row) in enumerate(df.iterrows()):
            if i % number_every == 0:
                ax.annotate(
                    str(row["elec_number"]),
                    (row["X"], row["Z"]),
                    xytext=(4, 4),
                    textcoords="offset points")
    return ax

def plot_weather_data(weather_df, start_date, end_date, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 4))

    # --- Precipitation (Left Axis) ---
    ax.bar(weather_df['date'], weather_df['rain'], width=1.0, color='tab:blue', alpha=0.7, label='Rain (mm)')
    
    if 'snow' in weather_df.columns and weather_df['snow'].sum() > 0:
        ax.bar(weather_df['date'], weather_df['snow'], width=1.0, color='tab:grey', alpha=0.7, label='Snow (cm)')
        ax.set_ylabel('Precipitation (mm/cm)')
    else:
        ax.set_ylabel('Precipitation (mm)')
        
    ax.legend(loc="upper left")
    ax.grid(True, ls='--', alpha=0.5)

    # --- Temperature (Right Axis) ---
    ax_temp = ax.twinx()

    # Convert dates to Matplotlib's numeric date representation
    # (LineCollection cannot directly handle datetime64 + float arrays)
    dates = mdates.date2num(weather_df["date"].to_numpy())
    temps = weather_df["temp"].to_numpy()

    # Build one line segment between each pair of consecutive measurements
    points = np.column_stack([dates, temps])
    segments = np.stack([points[:-1], points[1:]], axis=1)
    
    # Color each segment according to the temperature at its starting point (<0 is blue, >=0 is orange)
    colors = np.where(temps[:-1] < 0, "deepskyblue", "orange")

    lc = LineCollection(segments, colors=colors, linewidths=1.5, zorder=3)
    ax_temp.add_collection(lc)
    ax_temp.autoscale()
    ax_temp.axhline(0, color='grey', linestyle='--', linewidth=0.8, zorder=2)
    ax_temp.set_ylabel("Temperature (°C)")

    # --- Formatting ---
    ax.set_xlim([pd.to_datetime(start_date), pd.to_datetime(end_date)])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30)
    
    # Ensure the top layer (temperature) has a transparent background
    ax_temp.patch.set_visible(False)

    return ax, ax_temp

def extract_polygons(mesh):
    """Directly builds Matplotlib polygons from a PyGIMLi mesh."""
    polygons = []
    # cell.nodes() returns nodes in CCW order, perfect for Matplotlib
    for cell in mesh.cells():
        coords = [[node.x(), node.y()] for node in cell.nodes()]
        polygons.append(Polygon(coords, closed=True))
    return polygons

def plot_array_on_mesh(polygons, array=None, ax=None, **kwargs):
    """Plot an array of values on a collection of polygons.
    Additional keyword arguments are passed to ``PatchCollection``.
    Args:
        polygons: Collection of polygons to plot.
        array: Defaults to ``None``. Values associated with each polygon. 

    Keyword Args:
        top_offset: Padding in meters added above the mesh (default: 1.0).
        cmap: Colormap name, e.g. ``"viridis"`` or ``"Spectral_r"``.
        norm: Matplotlib normalization object.
        alpha: Transparency between 0 and 1.
        edgecolor: Polygon edge color, e.g. ``"black"`` or ``"none"``.
        facecolor: Polygon face color; usually unnecessary with ``values``.
        linewidth: Width of polygon edges.
        linestyle: Style of polygon edges.
    Returns:
        ax: Matplotlib axis object.
        collection: Matplotlib PatchCollection object.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 5))

    # Pop the offset parameter before kwargs gets passed to the collection
    top_offset = kwargs.pop('top_offset', 1.0)

    collection_kwargs = {
        'cmap': 'Spectral_r',
        'alpha': 0.9,
        'edgecolor': 'none',
        **kwargs,
    }

    collection = PatchCollection(polygons, **collection_kwargs)
    if array is not None:
        collection.set_array(np.asarray(array)) 

    ax.add_collection(collection)
    
    # Autoscale to fit the mesh perfectly, then add the extracted offset to the top
    ax.autoscale(axis='both', tight=True)
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(top=ymax + top_offset)
    
    ax.set_aspect('equal')
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Z (m)')
    
    return ax, collection