import pandas as pd
from pathlib import Path
from src.loaders.ert_loading_tools import *
from src.core.base import ProjectBase
import numpy as np

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

    def load_CR1000X(self, source: Path | str | list, pattern: str = "*.DAT", convert_VWC: bool = True) -> pd.DataFrame:
        files = self._resolve_files(source, pattern)
        if not files:
            raise FileNotFoundError(f"No files matching '{pattern}' found in {source}")
            
        for filepath in files:
            self.logger.info(f"Loading CR1000X file: {filepath.name}")

            # header is set after skiprow, in raw file 1st raw is metadata, 2nd row is column names, 3rd row is units and 4th is Smp
            df = pd.read_csv(filepath, sep=',', header=0, skiprows=[0, 2, 3])

            station_name = filepath.name[-12:-4] 
            df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], format="%Y-%m-%d %H:%M:%S", errors='coerce')
            cols = df.columns.difference(['TIMESTAMP'])
            df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')

            if convert_VWC:
                cols_VWC = [col for col in df.columns if 'Wat_Con' in col]
                for i, col in enumerate(cols_VWC):
                    soil_type = self.sensor_meta[station_name + "_type"].iloc[i]
                    params = self.conv_params[soil_type]
                    x = df[col].values
                    df[col] = df[col]

            self.file_dict[station_name] = df
            
        return self.file_dict
