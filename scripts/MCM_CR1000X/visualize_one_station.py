from src.loaders.sensor_loader import SensorLoader
from config.paths import ProjectPaths
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

def load_metadata(sensor_pos_path, conv_params_path):
    sensor_meta = pd.read_csv(sensor_pos_path, sep=';')
    conv_params = pd.read_csv(conv_params_path, sep=';', decimal=',')
    return sensor_meta, conv_params

paths = ProjectPaths(user='alexi', project_name='MCM_CR1000X') 

report_path = paths.OUTPUT_DIR / "MCM_CR1000X_1A_SL_S3" 
report_path.parent.mkdir(parents=True, exist_ok=True)
today = datetime.now().strftime("%Y%m%d")

sensor_meta, conv_params = load_metadata(paths.MCM_CR1000X_SENS_META, paths.MCM_CR1000X_CONV_PARAMS)

data = SensorLoader(site_id="MCM_CR1000X", sensor_meta=sensor_meta, conv_params=conv_params).load_CR1000X(paths.MCM_CR1000X_DATA)['1A_SL_S3']

plt.plot(data['TIMESTAMP'], data['Wat_Con_616(1)'])
plt.show()

