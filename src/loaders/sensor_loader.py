import re

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
            station = re.search(r"\d[AB]_(?:SL|PL)_[PS]\d?", filepath.name)
            if not station:
                raise FileNotFoundError(f"Couldn't extract station name from '{filepath.name}'")

            df = pd.read_csv(filepath, sep=",", skiprows=[0, 2, 3], low_memory=False)
            df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"], errors="coerce")
            df = df[df["TIMESTAMP"] >= pd.Timestamp("2020-01-01")] # Filter data befire 2020-01-01
            cols = df.columns.difference(["TIMESTAMP"])
            df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")

            name = station.group()
            self.file_dict[name] = (
                pd.concat([self.file_dict.get(name, pd.DataFrame()), df])
                .dropna(subset=["TIMESTAMP"])
                .drop_duplicates("TIMESTAMP", keep="last")
                .sort_values("TIMESTAMP")
                .reset_index(drop=True)
            )

        return self.file_dict

    def compute_vwc_CS616(self, station_name: str = None) -> pd.DataFrame:
        if station_name is None:
            station_names = list(self.file_dict.keys())
        else:
            station_names = [station_name]

        for station in station_names:    
            df = self.file_dict[station]

            cols_VWC = [col for col in df.columns if 'Wat_Con_616' in col]
            cols_Temp = [col for col in df.columns if 'SoilTemp' in col]
            for i, (col_vwc, col_temp) in enumerate(zip(cols_VWC, cols_Temp)):
                soil_type = self.sensor_meta[station]["CS616"]["soil_types"][i]
                sensor_depth = self.sensor_meta[station]["CS616"]["depths"][i]
                p = self.conv_params[soil_type]

                tau_m = df[col_vwc]
                T_sol = df[col_temp]

                # Apply time period measurement correction using measured temperature
                # tau_corr(tau_m, T_sol) = tau_m + (20 - T_sol)*(0.526 - 0.052 * tau_m + 0.00136 * tau_m**2) 
                tau_corr = tau_m + (20 - T_sol) * (0.526 - 0.052 * tau_m + 0.00136 * tau_m**2)
                
                vwc = (p["c1"] * tau_corr + p["c0"]) ** 2

                # Delete vwc values that are outside the valid range (0-0.7 m3/m3)
                vwc = np.clip(vwc, 0, 0.7)

                vwc = filter_vwc(vwc)

                df["VWC" + f"_{sensor_depth}"] = vwc
        
        return self.file_dict
