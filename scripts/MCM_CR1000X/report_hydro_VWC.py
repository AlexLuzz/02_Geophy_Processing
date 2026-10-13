from src.loaders.sensor_loader import SensorLoader
from src.visualization.HYDRO.hydro_stations_data_report import HydroDataReport
from config.paths import ProjectPaths
from datetime import datetime
import pandas as pd

def load_metadata(sensor_pos_path, conv_params_path):
    sensor_meta = pd.read_json(sensor_pos_path)
    conv_params = pd.read_json(conv_params_path)
    return sensor_meta, conv_params

paths = ProjectPaths(user='AQ96560', project_name='MCM_CR1000X') 

today = datetime.now().strftime("%Y%m%d_%HH%MM")

meta_1A, cal_CS616 = load_metadata(paths.MCM_CR1000X_1A_STATIONS_META, paths.MCM_CR1000X_CS616_CAL_WSP)

loader = SensorLoader(site_id="MCM_CR1000X", sensor_meta=meta_1A, conv_params=cal_CS616)
loader.load_CR1000X(paths.MCM_CR1000X_DATA_1A)
loader.compute_vwc_CS616()

HydroDataReport.print(
                    folder_path=paths.ACTIVE_PROJECT_DIR, 
                    sensor_loader=loader, 
                    sensor_metadata=meta_1A, 
                    filename=f"{today}_test.pdf")
