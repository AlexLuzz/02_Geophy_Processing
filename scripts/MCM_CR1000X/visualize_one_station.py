from src.loaders.sensor_loader import SensorLoader
from config.paths import ProjectPaths
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

def load_metadata(sensor_pos_path, conv_params_path):
    sensor_meta = pd.read_json(sensor_pos_path)
    conv_params = pd.read_json(conv_params_path)
    return sensor_meta, conv_params

paths = ProjectPaths(user='AQ96560', project_name='MCM_CR1000X') 

report_path = paths.OUTPUT_DIR / "MCM_CR1000X_1A_SL_S3" 
report_path.parent.mkdir(parents=True, exist_ok=True)
today = datetime.now().strftime("%Y%m%d")

meta_1A, cal_CS616 = load_metadata(paths.MCM_CR1000X_1A_STATIONS_META, paths.MCM_CR1000X_CS616_CAL_WSP)

loader = SensorLoader(site_id="MCM_CR1000X", sensor_meta=meta_1A, conv_params=cal_CS616)
loader.load_CR1000X(paths.MCM_CR1000X_DATA, pattern="MCM_1A_SL_P2.dat")

data = loader.compute_vwc_CS616("1A_SL_P2")

cols = [c for c in data.columns if c.startswith('VWC')]

for col in data.filter(like='VWC').columns:
    plt.plot(data['TIMESTAMP'], data[col], label=col)
plt.legend()
plt.show()

