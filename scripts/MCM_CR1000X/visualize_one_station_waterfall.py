from src.loaders.sensor_loader import SensorLoader
from config.paths import ProjectPaths
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
from scipy.interpolate import interp1d

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

data = data[
    (data["TIMESTAMP"] > start_date) &
    (data["TIMESTAMP"] < end_date)
]

cols = [c for c in data.columns if c.startswith('VWC')]
depths = pd.to_numeric([c.split('_')[-1] for c in cols])

data[cols] = data[cols].interpolate(axis=1, method="linear")

fig, ax = plt.subplots(figsize=(12, 5))

ticks = np.arange(0, 0.6, 0.05)
cmap = ListedColormap(plt.colormaps["jet_r"](np.linspace(0, 1, len(ticks))))
cmap.set_under("darkred")
cmap.set_over("navy")
norm = BoundaryNorm(ticks, cmap.N)

depth_grid = np.linspace(min(depths), max(depths), 100)
Z = interp1d(depths, data[cols].T, axis=0, kind="linear", bounds_error=False, fill_value="extrapolate")(depth_grid)

mesh = ax.pcolormesh(
    data["TIMESTAMP"],
    depth_grid,
    Z,
    shading="auto",
    cmap=cmap,
    norm=norm
)

cbar = fig.colorbar(mesh, ax=ax, ticks=ticks, extend="both")
cbar.set_label("Volumetric water content (VWC)")

# Axes
ax.set_xlabel("Time")
ax.set_xlim(start_date, end_date)
ax.set_ylabel("Depth (cm)")

# Usually useful for soil depth:
ax.invert_yaxis()

fig.autofmt_xdate()

plt.legend()
plt.show()

