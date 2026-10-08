import pandas as pd
from pathlib import Path
from src.loaders.ert_loading_tools import *
from src.core.base import ProjectBase
from src.processing.data.filtration_tools import get_hampel_mask
import numpy as np

def filter_vwc(s, max_change=0.03):
    bad = s.diff().abs().gt(max_change) | s.diff(-1).abs().gt(max_change)
    return s.mask(bad)

class SensorLoader(ProjectBase):
    """Data loader for CR1000X sensor files"""

    def __init__(
        self,
        site_id: str,
        sensor_meta: pd.DataFrame = None,
        conv_params: pd.DataFrame = None,

        ):
        super().__init__()
        self.site_id = site_id
        
        self.sensor_meta = sensor_meta
        self.conv_params = conv_params

        self.file_dict = {}

        self.logger.info(
            f"Initialized SensorLoader for site: '{self.site_id}'"
        )

    def load_CR1000X(self, source: Path | str | list, pattern: str = "*.dat") -> pd.DataFrame:
        files = self._resolve_files(source, pattern)
        if not files:
            raise FileNotFoundError(f"No files matching '{pattern}' found in {source}")
            
        for filepath in files:
            self.logger.info(f"Loading CR1000X file: {filepath.name}")

            # header is set after skiprow, in raw file 1st raw is metadata, 2nd row is column names, 3rd row is units and 4th is Smp
            df = pd.read_csv(filepath, sep=',', header=0, skiprows=[0, 2, 3], low_memory=False)

            station_name = filepath.name[-12:-4] 
            df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], format="%Y-%m-%d %H:%M:%S", errors='coerce')
            cols = df.columns.difference(['TIMESTAMP'])
            df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')

            self.file_dict[station_name] = df
            
        return self.file_dict

    def compute_vwc_CS616(self, station_name: str) -> pd.DataFrame:
        df = self.file_dict[station_name]

        cols_VWC = [col for col in df.columns if 'Wat_Con_616' in col]
        cols_Temp = [col for col in df.columns if 'SoilTemp' in col]
        for i, (col_vwc, col_temp) in enumerate(zip(cols_VWC, cols_Temp)):
            soil_type = self.sensor_meta[station_name]["CS616"]["soil_types"][i]
            sensor_depth = self.sensor_meta[station_name]["CS616"]["depths"][i]
            p = self.conv_params[soil_type]

            tau_m = df[col_vwc]
            T_sol = df[col_temp]

            # Apply time period measurement correction using measured temperature
            # tau_corr(tau_m, T_sol) = tau_m + (20 - T_sol)*(0.526 - 0.052 * tau_m + 0.00136 * tau_m**2) 
            tau_corr = tau_m + (20 - T_sol) * (0.526 - 0.052 * tau_m + 0.00136 * tau_m**2)
            
            vwc = (p["c1"] * tau_corr + p["c0"]) ** 2

            # Delete vwc values that are outside the valid range (0-0.6 m3/m3)
            vwc = np.clip(vwc, 0, 0.5)

            vwc = filter_vwc(vwc)

            df["VWC" + f"_{sensor_depth}"] = vwc
        
        return df
