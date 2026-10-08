from pathlib import Path
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np

from src.core.base import ProjectBase

class DASLoader(ProjectBase):
    """Data loader for Distributed Acoustic Sensing (DAS) NetCDF files."""

    def __init__(self, site_id: str):
        super().__init__()
        self.site_id = site_id
        self.dataset = None
        
        self.logger.info(f"Initialized DASLoader for site: '{self.site_id}'.")

    def load_nc(self, source: Path | str | list, pattern: str = "*.nc", use_dask: bool = True) -> xr.Dataset:
        """
        Loads NetCDF files lazily. 
        Setting use_dask=True allows terabytes of data to be parsed instantly without filling RAM.
        """
        files = self._resolve_files(source, pattern)
        if not files:
            raise FileNotFoundError(f"No files matching '{pattern}' found in {source}")

        self.logger.info(f"Loading {len(files)} DAS NetCDF file(s)...")

        # Scalability Key: 'chunks="auto"' tells Dask to manage RAM dynamically
        chunks = "auto" if use_dask else None
        
        if len(files) == 1:
            self.dataset = xr.open_dataset(files[0], chunks=chunks)
        else:
            # open_mfdataset seamlessly stitches hundreds of .nc files together along the time dimension
            self.dataset = xr.open_mfdataset(files, chunks=chunks, combine="by_coords")

        self.logger.info(f"DAS Data Loaded. Dimensions: {dict(self.dataset.dims)}")
        return self.dataset

    def inspect_metadata(self, print_summary: bool = True) -> dict:
        """
        Scans the loaded NetCDF file and extracts dimensions, coordinates, 
        and variable structures without loading the heavy arrays into RAM.
        """
        if self.dataset is None:
            raise ValueError("Dataset not loaded. Call load_nc() first.")

        ds = self.dataset
        
        metadata = {
            "dimensions": dict(ds.dims),
            "coordinates": list(ds.coords.keys()),
            "variables": {},
            "global_attributes": dict(ds.attrs)
        }

        if print_summary:
            self.logger.info("--- DAS NetCDF Structure Summary ---")
            self.logger.info(f"Dimensions: {metadata['dimensions']}")
            self.logger.info(f"Coordinates: {metadata['coordinates']}")

        for var_name, var_data in ds.data_vars.items():
            var_info = {
                "shape": var_data.shape,
                "dimensions": var_data.dims,
                "dtype": str(var_data.dtype),
                "attributes": dict(var_data.attrs)
            }
            metadata["variables"][var_name] = var_info
            
            if print_summary:
                self.logger.info(f"Var: '{var_name}' | Shape: {var_info['shape']} | Type: {var_info['dtype']}")
                
                # Fetch a tiny 5-element snippet of the actual data to see what the numbers look like
                try:
                    # Slices the first index of all dimensions except the last one, grabbing 5 values
                    slice_dict = {dim: 0 for dim in var_data.dims[:-1]}
                    slice_dict[var_data.dims[-1]] = slice(0, 5)
                    data_snippet = var_data.isel(**slice_dict).values
                    self.logger.info(f"     Preview -> {data_snippet}")
                except Exception:
                    self.logger.info(f"     Preview -> [Cannot extract snippet safely]")

        return metadata

    def plot_waterfall(self, data_var, ax=None, time_slice=None, distance_slice=None,
                   cmap="RdBu_r", robust=True):
        if data_var not in self.dataset.data_vars:
            raise KeyError(f"Variable '{data_var}' not found. Available: {list(self.dataset.data_vars)}")

        data = self.dataset[data_var]

        if time_slice is not None:
            data = data.isel(time=time_slice)
        if distance_slice is not None:
            data = data.isel(channels=distance_slice)

        data = data.compute()

        if ax is None:
            _, ax = plt.subplots(figsize=(12, 6))

        data.plot(ax=ax, cmap=cmap, robust=robust)
        ax.set_xlabel("Time")
        ax.set_ylabel("Channel")

        return ax