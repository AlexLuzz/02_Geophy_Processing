import pandas as pd
from pathlib import Path
from datetime import datetime
import re
from src.loaders.ert_loading_tools import *
from src.core.base import ProjectBase
import numpy as np

class ERTLoader(ProjectBase):
    """Data loader for ERT instruments"""

    def __init__(
        self,
        site_id: str,
        elec_pos: pd.DataFrame,
        ):
        super().__init__()
        self.site_id = site_id
        
        if elec_pos is None or elec_pos.empty:
            raise ValueError("Electrode positions (elec_pos) are strictly required.")
        self.elec_pos = elec_pos

        self.raw_data = pd.DataFrame()
        self.data = pd.DataFrame()

        self.logger.info(
            f"Initialized ERTLoader for site: '{self.site_id}' with"
            f" {len(self.elec_pos)} electrodes loaded."
        )
        
        self.ERT_COLS = {
        'A': 'Int64', 
        'B': 'Int64', 
        'M': 'Int64', 
        'N': 'Int64',
        'R (Ohm)': float, 
        'Vmn (mV)': float, 
        'Iab (mA)': float, 
        'Tx (V)': float,
        'R_ab (kOhm)': float, 
        'k (m)': float, 
        'rhoa (Ohm.m)': float,
        'err_stk (%)': float,
        'date_survey': 'datetime64[ns]', 
        'date_meas': 'datetime64[ns]',
        'site_id': str, 'hardware_id': str,
        }

    def finalize_standardization(self) -> pd.DataFrame:
        df = self.raw_data.copy()
        self.logger.info("--- Starting Global Standardization ---")

        # 1. Apply class-level identifiers and order
        df['site_id'] = self.site_id
        df = df.sort_values(by='date_meas').reset_index(drop=True)

        # 2. Geometric factors & rhoa (elec_pos is guaranteed to exist)
        df = compute_geometric_factors(df, self.elec_pos)
        df['rhoa (Ohm.m)'] = df['k (m)'] * df['R (Ohm)']

        # 3. Reciprocal Masking & Error Processing
        df['reciprocal'] = get_reciprocal_mask_vectorized(df)
        df = process_reciprocals(df)

        # 4. Type Casting and Missing Column Logging
        final_types = self.ERT_COLS.copy()
        final_types['reciprocal'] = bool
        final_types['err_rec (%)'] = float
        
        for col, dtype in final_types.items():
            if col not in df.columns:
                self.logger.warning(f"Column '{col}' is missing. Padding with NAs.")
                df[col] = pd.NA
                
            if dtype == 'datetime64[ns]':
                df[col] = pd.to_datetime(df[col]) 
            elif dtype == str:
                df[col] = df[col].astype(str).replace({'nan': pd.NA, '<NA>': pd.NA, 'None': pd.NA})
            else:
                df[col] = pd.to_numeric(df[col]).astype(dtype)

        # 5. Whitelist
        df = df[list(final_types.keys())]
        self.data = df
        
        # 6. Global Stat Extraction (Fails loud if ERT fundamentals are missing)
        num_meas = len(df)
        recip_count = df['reciprocal'].sum()
        elecs = sorted([int(e) for e in pd.unique(df[['A', 'B', 'M', 'N']].values.ravel()) if pd.notna(e)])
        elec_log = f"{len(elecs)} total (Range: {min(elecs)} to {max(elecs)})"
        
        rhoa_valid = df['rhoa (Ohm.m)'].dropna()
        rhoa_stats = f"Min: {rhoa_valid.min():.2f}, Max: {rhoa_valid.max():.2f}"
        
        self.logger.info(f"  Total Meas   : {num_meas} ({recip_count} Reciprocals)")
        self.logger.info(f"  Electrodes   : {elec_log}")
        self.logger.info(f"  rhoa stats   : {rhoa_stats}")
        self.logger.info("---------------------------------------")
        
        return self.data

    def load_prime(self, source: Path | str | list, pattern: str = "*.tab", standardize: bool = True, offset_elec: int = 0) -> pd.DataFrame:
        files = self._resolve_files(source, pattern)
        if not files:
            raise FileNotFoundError(f"No files matching '{pattern}' found in {source}")
            
        file_dfs = []
        for filepath in files:
            self.logger.info(f"Loading Prime file: {filepath.name}")
            data_start, metadata = scan_header(filepath, data_start_markers=['pt_line_number:', 'pt_calc_res:'])
            
            start_time_str = metadata.get('set_actual_start_time')
            if not start_time_str:
                raise ValueError(f"No start time metadata extracted in {filepath.name}")
                    
            df = pd.read_csv(filepath, skiprows=data_start, sep=r'\s+')
            df.columns = df.columns.str.strip()
            
            df = df.rename(columns={
                'pt_c1_no:': 'A', 'pt_c2_no:': 'B', 'pt_p1_no:': 'M', 'pt_p2_no:': 'N',
                'pt_calc_res:': 'R (Ohm)', 'pt_meas_voltage_mean:': 'Vmn (mV)', 
                'pt_meas_current_mag:': 'Iab (mA)', 'pt_meas_applied_voltage:': 'Tx (V)', 
                'pt_meas_contact_resistance:': 'R_ab (kOhm)', 'pt_calc_res_error:': 'err_stk (%)', 
                'pt_time:': 'date_meas'
            })

            if offset_elec != 0:
                cols = ['A', 'B', 'M', 'N']
                df[cols] = df[cols].apply(pd.to_numeric, errors='raise') + offset_elec
                self.logger.info(f" -> Applied electrode offset of {offset_elec} to {filepath.name}")
            
            df['hardware_id'] = 'Prime'
            df['date_survey'] = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")

            file_dfs.append(df)

        new_data = pd.concat(file_dfs, ignore_index=True)
        self.raw_data = new_data if self.raw_data.empty else pd.concat([self.raw_data, new_data], ignore_index=True)

        if standardize:
            self.finalize_standardization()
            
        return self.data

    def load_sas4000(self, source: Path | str | list, pattern: str = "*.AMP", standardize: bool = True) -> pd.DataFrame:
        files = self._resolve_files(source, pattern)
        if not files:
            raise FileNotFoundError(f"No files matching '{pattern}' found in {source}")
            
        file_dfs = []
        for filepath in files:
            self.logger.info(f"Loading SAS4000 file: {filepath.name}")
            data_start, metadata = scan_header(filepath, data_start_markers=['No.', 'A(x)'])
            
            start_time_str = metadata.get('Date & Time')
            if not start_time_str:
                raise ValueError(f"No 'Date & Time' metadata extracted in {filepath.name}")
            survey_date = datetime.strptime(start_time_str, "%d/%m/%Y %H:%M:%S")
                    
            df = pd.read_csv(filepath, skiprows=data_start, sep=r'\s+')
            
            if 'Voltage(V)' not in df.columns:
                raise KeyError(f"'Voltage(V)' column is missing in {filepath.name}")
            
            df['Voltage(V)'] = df['Voltage(V)'] * 1000.0
            self.logger.info(f" -> Converted Voltage(V) to mV for {filepath.name}")
            
            df = df.rename(columns={
                'A(x)': 'A', 'B(x)': 'B', 'M(x)': 'M', 'N(x)': 'N',
                'Res.(ohm)': 'R (Ohm)', 'Voltage(V)': 'Vmn (mV)', 'I(mA)': 'Iab (mA)', 'Error(%)': 'err_stk (%)'
            })
            
            df['err_stk (%)'] = pd.to_numeric(df['err_stk (%)'].replace('1.#QNAN0', np.nan))
            df = df[~df['A'].astype(str).isin(['32767', '32767.0'])]
            df['date_meas'] = survey_date + pd.to_timedelta(pd.to_numeric(df['Time']), unit='s')

            df = split_sas4000_surveys(df, time_gap_hours=0.25)
            df['hardware_id'] = 'SAS4000'

            file_dfs.append(df)

        new_data = pd.concat(file_dfs, ignore_index=True)
        self.raw_data = new_data if self.raw_data.empty else pd.concat([self.raw_data, new_data], ignore_index=True)

        if standardize:
            self.finalize_standardization()
            
        return self.data

    def load_ohmpi(self, source: Path | str | list, pattern: str = "*.csv", standardize: bool = True) -> pd.DataFrame:
        files = self._resolve_files(source, pattern)
        if not files:
            raise FileNotFoundError(f"No files matching '{pattern}' found in {source}")
            
        file_dfs = []
        for filepath in files:
            self.logger.info(f"Loading OhmPi file: {filepath.name}")
            df = pd.read_csv(filepath, sep=',')
            
            date_match = re.search(r'\d{8}T\d{6}', filepath.stem)
            if not date_match:
                raise ValueError(f"Cannot extract survey date from filename {filepath.name}")
            df['date_survey'] = datetime.strptime(date_match.group(), "%Y%m%dT%H%M%S")

            df = df.rename(columns={
                'R [Ohm]': 'R (Ohm)', 'Vmn [mV]': 'Vmn (mV)', 'I [mA]': 'Iab (mA)',
                'Tx [V]': 'Tx (V)', 'R_ab [kOhm]': 'R_ab (kOhm)',
                'time': 'date_meas', 'R_std [%]': 'err_stk (%)', 
            })
            
            df['hardware_id'] = 'OhmPi'
            
            file_dfs.append(df)

        new_data = pd.concat(file_dfs, ignore_index=True)
        self.raw_data = new_data if self.raw_data.empty else pd.concat([self.raw_data, new_data], ignore_index=True)

        if standardize:
            self.finalize_standardization()
            
        return self.data