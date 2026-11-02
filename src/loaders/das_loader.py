
from pathlib import Path

import h5py
import xarray as xr
import numpy as np

from src.core.base import ProjectBase


class DASLoader(ProjectBase):

    def __init__(self, site_id: str):
        super().__init__()
        self.site_id = site_id
        self.dataset = None

    def load_nc(
        self,
        source: Path | str | list,
        pattern: str = "*.nc",
        use_dask: bool = True,
    ):
        files = self._resolve_files(source, pattern)
        if not files:
            raise FileNotFoundError(f"No files matching {pattern} in {source}")

        self.close()
        chunks = "auto" if use_dask else None
        self.dataset = (
            xr.open_dataset(files[0], chunks=chunks)
            if len(files) == 1
            else xr.open_mfdataset(files, chunks=chunks, combine="by_coords")
        )
        return self.dataset

    def load_h5(self, source: Path | str | list, pattern: str = "*.h5"):
        files = self._resolve_files(source, pattern)
        if not files:
            raise FileNotFoundError(f"No files matching {pattern} in {source}")

        self.close()
        self.dataset = h5py.File(files[0], "r") if len(files) == 1 else [
            h5py.File(file, "r") for file in files
        ]
        return self.dataset

    def retrieve_febus_h5(self, show: bool = False):
        metadata = {}
        data = {}
        with self.dataset as f:
            def check_and_show(name, obj):
                if show:
                    print(f"\n{'GROUP' if isinstance(obj, h5py.Group) else 'DATASET'}: /{name}")
                for key, value in obj.attrs.items():
                    if show:
                        print(f"  @{key} = {value}")
                    metadata[key] = value
                if isinstance(obj, h5py.Dataset):
                    if show:
                        print(f"  shape={obj.shape}, dtype={obj.dtype}")
                    data[name] = np.array(obj)
            if show:
                print("FILE ATTRIBUTES:", dict(f.attrs))
            f.visititems(check_and_show)
        return metadata, data


    def close(self):
        if isinstance(self.dataset, list):
            for dataset in self.dataset:
                dataset.close()
        elif self.dataset is not None:
            self.dataset.close()
        self.dataset = None
