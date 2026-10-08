from src.loaders.sensor_loader import SensorLoader
from config.paths import ProjectPaths
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
from scipy.interpolate import interp1d
from scipy.interpolate import griddata
import matplotlib.dates as mdates

def load_metadata(sensor_pos_path, conv_params_path):
    sensor_meta = pd.read_csv(sensor_pos_path, sep=';')
    conv_params = pd.read_csv(conv_params_path, sep=';', decimal=',')
    return sensor_meta, conv_params

paths = ProjectPaths(user='AQ96560', project_name='MCM_CR1000X') 

report_path = paths.OUTPUT_DIR / "MCM_CR1000X_1A_SL_S3" 
report_path.parent.mkdir(parents=True, exist_ok=True)
today = datetime.now().strftime("%Y%m%d")

sensor_meta, conv_params = load_metadata(paths.MCM_CR1000X_SENS_META, paths.MCM_CR1000X_CONV_PARAMS)

data = SensorLoader(site_id="MCM_CR1000X", sensor_meta=sensor_meta, conv_params=conv_params).load_CR1000X(paths.MCM_CR1000X_DATA, pattern="MCM_1A_SL_P2.dat")['1A_SL_P2']

start_date = datetime(2020, 12, 1)
end_date = datetime(2021, 10, 15)

df = data[(data["TIMESTAMP"] >= start_date) & (data["TIMESTAMP"] <= end_date)].copy()

# 2. Resample to daily mean to eliminate sub-daily logger noise
cols = [c for c in df.columns if c.startswith("VWC")]
depths = np.array([float(c.split("_")[-1]) for c in cols])

df = df.set_index("TIMESTAMP")[cols].resample("1D").mean()

# 3. Create regular 2D grid for contouring (Time x Depth)
timestamps = df.index
time_nums = mdates.date2num(timestamps)

# Fine grid
time_grid_num = np.linspace(time_nums.min(), time_nums.max(), 300)
depth_grid = np.linspace(0, 260, 260)
T_grid, D_grid = np.meshgrid(time_grid_num, depth_grid)

# Flatten points for 2D interpolation (retaining NaNs where probes died)
points = []
values = []
for t_idx, t_val in enumerate(time_nums):
    for d_idx, d_val in enumerate(depths):
        val = df.iloc[t_idx, d_idx]
        if not np.isnan(val):
            points.append((t_val, d_val))
            values.append(val)

# Linear 2D interpolation (keeps areas with no surrounding data as NaN/white)
Z_grid = griddata(points, values, (T_grid, D_grid), method="linear")

# 4. Colormap & Contour Levels (matching Tecplot legend: 0.05 to 0.50)
levels = np.array([0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50])

# Tecplot-style rainbow: Red -> Orange -> Yellow -> Green -> Cyan -> Blue -> Navy
cmap = ListedColormap([
    "#ff0000",  # Red (< 0.05 - 0.10)
    "#ff8000",  # Orange (0.10 - 0.15)
    "#ffff00",  # Yellow (0.15 - 0.20)
    "#80ff00",  # Light green (0.20 - 0.25)
    "#00cc00",  # Green (0.25 - 0.30)
    "#00ffff",  # Cyan (0.30 - 0.35)
    "#0099ff",  # Sky blue (0.35 - 0.40)
    "#0033ff",  # Medium blue (0.40 - 0.45)
    "#000080",  # Navy (> 0.45)
])

# 5. Plotting
fig, ax = plt.subplots(figsize=(11, 6), dpi=150)

time_grid_dates = mdates.num2date(time_grid_num)
T_plot, D_plot = np.meshgrid(time_grid_dates, depth_grid)

# Use contourf instead of pcolormesh
cf = ax.contourf(
    T_plot,
    D_plot,
    Z_grid,
    levels=levels,
    cmap=cmap,
    extend="both"
)

# 6. Formatting & Soil Layer Boundaries
ax.set_ylim(260, 0)  # Invert so depth 0 is at the top
ax.set_ylabel("Depth (cm)", fontsize=11, fontweight="bold")

# Add horizontal geological layer division lines and text annotations
layers = [
    (18, "Topsoil"),
    (53, "Uncompacted Overburden"),
    (128, "Compacted Overburden"),
    (135, "Waste Rock"),
]

for y_depth, label in layers:
    if y_depth <= 128:
        ax.axhline(y_depth, color="black", linewidth=1.2)
    ax.text(
        mdates.date2num(start_date) + 2,
        y_depth - 3 if y_depth <= 128 else y_depth + 6,
        label,
        fontsize=9,
        fontweight="bold",
        color="black",
        va="center",
    )

# Date formatting
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b-%y"))
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontweight="bold")

# Horizontal Colorbar matching the Tecplot layout
cbar = fig.colorbar(cf, ax=ax, orientation="horizontal", pad=0.15, aspect=35, shrink=0.7)
cbar.set_label("Volumetric Water Content (m3/m3)", fontsize=10)
cbar.set_ticks(levels)

plt.tight_layout()
plt.show()
