# Complete Architecture & Quality Audit: `02_Geophy_Processing`

**Target Directory:** `C:\Users\AQ96560\OneDrive - ETS\01_Coding\02_Geophy_Processing`

## 1. Directory Tree & Module Signatures

### `code_diagnosis\architecture_audit.py`

**Functions:**
- `def analyze_python_file(file_path)` — *Extracts imports, classes, and functions using AST.*
- `def run_external_tool(module_name, args)` — *Runs a Python module tool using the current Python environment.*
- `def build_full_audit(target_dir, output_file, ignore_dirs)`

---

### `code_diagnosis\generate_architecture.py`

**Functions:**
- `def extract_signatures(file_path)` — *Extracts top-level and class-level definitions from a Python file using AST.*
- `def generate_full_architecture(root_dir, output_file, ignore_dirs)`

---

### `code_diagnosis\generate_enhanced_architecture.py`

**Functions:**
- `def analyze_python_file(file_path)` — *Parses a Python file to extract imports, class/method hierarchies, and functions.*
- `def generate_deep_architecture_report(root_dir, output_file, ignore_dirs)`

---

### `code_diagnosis\generate_tree.py`

**Functions:**
- `def save_tree_to_file(root_dir, output_file, ignore_dirs)`

---

### `config\paths.py`

**Classes:**
- `class ProjectPaths` (1 methods) — *Centralized, READ-ONLY path management for raw ERT data.*
  - `def __init__(self, user, project_name)`

---

### `main.py`

**Dependencies:**
- *Third-party:* `config, src`

---

### `scripts\ERT_useful\clean_vec_pycache.py`

**Functions:**
- `def cleanup(root)`

---

### `scripts\ERT_useful\prime_survey_building.py`

**Dependencies:**
- *Third-party:* `config, matplotlib, numpy, pandas, pygimli, src`

**Functions:**
- `def plot_pseudo_doi(dataContainer, array_type)` — *Plots the pseudo-section points for ERT data.*

---

### `scripts\ERT_useful\prime_survey_building_V2.py`

**Dependencies:**
- *Third-party:* `config, matplotlib, numpy, pandas, pygimli, src`

**Functions:**
- `def plot_pseudo_doi(dataContainer, array_type)` — *Plots the pseudo-section points for ERT data.*

---

### `scripts\MCM_GEO\GEO_data_filter.py`

**Dependencies:**
- *Third-party:* `config, src`

**Functions:**
- `def filter_GEO(dd, sc, rec_err, plot_report)`

---

### `scripts\MCM_GEO\GEO_gmsh.py`

**Dependencies:**
- *Third-party:* `config, gmsh, matplotlib, numpy, pandas, pygimli, src`

**Functions:**
- `def build_gmsh_layered(df, depth, interface_depth, extension, size_surface, size_interface, size_depth, params)` — *Builds a 2D ERT mesh with a distinct structural interface (e.g., overburden vs tailings)*
- `def build_MCM_GEO(show)`

---

### `scripts\MCM_GEO\GEO_plot_report.py`

**Dependencies:**
- *Third-party:* `config, src`

**Functions:**
- `def run_GEO()`

---

### `scripts\MCM_GEO\GEO_single_survey_ensemble_inv.py`

**Dependencies:**
- *Third-party:* `GEO_gmsh, config, scripts, src`

**Functions:**
- `def run_GEO(dd, sc, rec_err)`

---

### `scripts\MCM_GEO\GEO_single_survey_inv.py`

**Dependencies:**
- *Third-party:* `GEO_gmsh, config, scripts, src`

**Functions:**
- `def run_GEO()`

---

### `scripts\MCM_MONOS\mesh_building\MONO_gmsh.py`

**Dependencies:**
- *Third-party:* `config, gmsh, matplotlib, numpy, pandas, pygimli, src`

**Functions:**
- `def build_gmsh_layered(df, depth, interface_depth, extension, size_surface, size_interface, size_depth, params)` — *Builds a 2D ERT mesh with a distinct structural interface (e.g., overburden vs tailings)*
- `def test_build_MCM_M2m()`

---

### `scripts\MCM_MONOS\MONO1M_single_survey_inv.py`

**Dependencies:**
- *Third-party:* `config, scripts, src`

**Functions:**
- `def run_MONO1M()`

---

### `scripts\MCM_MONOS\MONO1M_timelapse_inv.py`

**Dependencies:**
- *Third-party:* `config, scripts, src`

**Functions:**
- `def run_TL_MONO1M()`

---

### `scripts\MCM_MONOS\MONO2M_data_filter.py`

**Dependencies:**
- *Third-party:* `config, src`

---

### `scripts\MCM_MONOS\MONO2M_single_inv_flat_topo.py`

**Dependencies:**
- *Third-party:* `config, matplotlib, numpy, src`

---

### `scripts\MCM_MONOS\MONO2M_single_survey_inv.py`

**Dependencies:**
- *Third-party:* `config, scripts, src`

**Functions:**
- `def run_MONO2M()`

---

### `scripts\MCM_MONOS\MONO2M_timelapse_inv.py`

**Dependencies:**
- *Third-party:* `config, scripts, src`

**Functions:**
- `def run_TL_MONO2M()`

---

### `scripts\MCM_MONOS\MONOS_rawData_TLERT_report.py`

**Dependencies:**
- *Third-party:* `config, pandas, src`

**Functions:**
- `def process_ert_site(site_id, geom_path, source_paths, offset_elec)` — *Helper function to load geometry, parse PRIME data, and export the raw data report.*

---

### `scripts\MCM_MONOS\plot_report.py`

**Dependencies:**
- *Third-party:* `config, src`

**Functions:**
- `def run_plot_mono1m()`

---

### `scripts\MCM_MONOS\run_both.py`

**Dependencies:**
- *Third-party:* `MONO1M_single_survey_inv, MONO1M_timelapse_inv, MONO2M_single_survey_inv, MONO2M_timelapse_inv`

---

### `scripts\Weather\find_station.py`

**Dependencies:**
- *Third-party:* `requests`

**Functions:**
- `def get_stations_dict(province, search_term)`

---

### `scripts\Weather\plot_weather.py`

**Dependencies:**
- *Third-party:* `matplotlib, pandas, src`

---

### `src\__init__.py`

---

### `src\core\__init__.py`

---

### `src\core\base.py`

**Dependencies:**
- *Third-party:* `h5py, numpy, pandas, src`

**Classes:**
- `class MemoryHandler` (2 methods)
  - `def __init__(self)`
  - `def emit(self, record)`
- `class ProjectBase` (8 methods)
  - `def __init__(self, memory)`
  - `def _setup_logging(self, memory)`
  - `def load(self, file_path)`
  - `def load_results(self, folder_path)`
  - `def _prepare_h5_value(self, key, val)`
  - `def save(self, data, file_path, metadata)`
  - `def save_mesh(self, mesh, file_path)`
  - `def load_mesh(self, file_path)`

---

### `src\loaders\__init__.py`

---

### `src\loaders\ert_loader.py`

**Dependencies:**
- *Third-party:* `numpy, pandas, src`

**Classes:**
- `class ERTLoader` (6 methods) — *Data loader for ERT instruments*
  - `def __init__(self, site_id, elec_pos)`
  - `def _resolve_files(self, source, pattern)`
  - `def finalize_standardization(self)`
  - `def load_prime(self, source, pattern, standardize, offset_elec)`
  - `def load_sas4000(self, source, pattern, standardize)`
  - `def load_ohmpi(self, source, pattern, standardize)`

---

### `src\loaders\ert_loading_tools.py`

**Dependencies:**
- *Third-party:* `numpy, pandas`

**Functions:**
- `def scan_header(filepath, data_start_markers, delimiter, keys_to_keep)` — *Scans a text file to extract specific metadata and find the data starting line.*
- `def split_sas4000_surveys(df, time_gap_hours)` — *Detects multiple surveys within a single dataframe by looking for time *
- `def pygimli_compute_geometric_factors(df, df_elec_pos)` — *Compute geometric factors using PyGIMLi.*
- `def compute_geometric_factors(df, df_elec_pos)` — *Compute geometric factors using 3D Euclidean distances.*
- `def get_reciprocal_mask(df)` — *Identify reciprocal ERT measurements by following acquisition order.*
- `def get_reciprocal_mask_vectorized(df)` — *Identify reciprocal ERT measurements based on alternating occurrences*
- `def process_reciprocals(df)` — *Flips reciprocal dipoles to match forward configurations, isolates true *
- `def load_geometry(filepath, params)` — *Load and process electrode geometry.*

---

### `src\loaders\weather_loading_tools.py`

**Dependencies:**
- *Third-party:* `pandas, requests`

**Functions:**
- `def fetch_weather_data(start_date, end_date, station_id, freq)` — *Fetches daily weather data from Environment Canada and resamples to desired frequency.*

---

### `src\mesh\__init__.py`

---

### `src\mesh\gmesh_tools.py`

**Dependencies:**
- *Third-party:* `gmsh, pandas, pygimli`

**Functions:**
- `def build_gmsh_mesh(df, depth, extension, size_surface, size_depth, params, out_path)` — *Build an unstructured X-Z mesh using Gmsh tailored for PyGIMLi.*
- `def build_gmsh_mono2m(df, depth, extension, size_surface, size_depth, params)`

---

### `src\mesh\pygimli_mesh_tools.py`

**Dependencies:**
- *Third-party:* `numpy, pygimli, scipy`

**Functions:**
- `def build_grid_mesh(x_min, x_max, y_min, y_max, dx, dy)` — *Creates a structured quadrilateral grid.*
- `def build_unstructured_mesh(df, surface_offset, depth, extension, refine_dist)` — *Create an unstructured triangular mesh from electrode positions with *
- `def safe_mesh_save(mesh, target_path)` — *Saves a PyGIMLi mesh by bypassing Windows/C++ long path and accent limits.*
- `def safe_mesh_load(source_path)` — *Loads a PyGIMLi mesh bypassing Windows/C++ encoding and path limits.*
- `def build_mono2m_plc(df, layer_depth, depth, extension, markers, area_top, area_bottom, curved_bottom)` — *Helper: Builds the core layered polygons and fuses them with explicit area constraints.*
- `def build_mono2m_meshes(df, layer_depth, depth, extension, area_top, area_bottom, quality, add_boundary, bound_ext, bound_depth, start_markers)` — *Builds both the inversion mesh and the starting model mesh simultaneously *
- `def build_starting_model(mesh, para_domain, rhomap, default_res)` — *Maps resistivity values from a fine start mesh to the para_domain using a rhomap.*

---

### `src\processing\__init__.py`

---

### `src\processing\data\__init__.py`

---

### `src\processing\data\data_preparator.py`

**Dependencies:**
- *Third-party:* `pandas, src`

**Classes:**
- `class DataPreparator` (4 methods)
  - `def __init__(self)`
  - `def filter_mono2m_custom(self, df, min_v, max_err)`
  - `def filter_standard_survey(self, df, thresholds)`
  - `def print_logs(self)`

**Functions:**
- `def log_filtration(func)` — *Decorator to automatically log dropped measurements and top affected A-B pairs.*

---

### `src\processing\data\data_tools.py`

**Dependencies:**
- *Third-party:* `numpy, pandas`

**Functions:**
- `def resample_timeseries(df, freq_hours, max_gap_hours, timestamp_col, config_cols, meas_cols)` — *Resamples data and interpolates missing values strictly bounded by max_gap_hours.*
- `def interpolate_excluded_period(df, electrodes, start_date, end_date, date_col, cols_to_interp, config_cols)` — *Finds measurements containing specific electrodes during a time window, *
- `def filter_common_measurements(df, config_cols, date_col)` — *Ensures every survey has the exact same length by keeping only the *

---

### `src\processing\data\filtration_tools.py`

**Dependencies:**
- *Third-party:* `numpy, pandas`

**Functions:**
- `def get_date_range_mask(df, start_date, end_date, return_df, date_col)` — *Returns True for rows where the date is within the specified range.*
- `def get_threshold_mask(df, col, min_val, max_val)` — *Returns True for values strictly within the min/max bounds.*
- `def get_excluded_elecs_mask(df, excluded_elecs, config_cols)` — *Returns False if any electrode in the configuration is in the excluded list.*
- `def get_excluded_configs_mask(df, excluded_configs, config_cols)` — *Returns False for exact A, B, M, N configuration matches.*
- `def get_hampel_mask(df, target_col, window_size, n_sigma, config_cols)` — *Vectorized Hampel filter. Returns False for outliers detected within the rolling window.*
- `def get_discontinued_configs_mask(df, min_length, config_cols)` — *Returns False for electrode configurations that have fewer total measurements than min_length.*

---

### `src\processing\inversion\__init__.py`

---

### `src\processing\inversion\ert_processor.py`

**Dependencies:**
- *Third-party:* `numpy, pandas, pygimli, src`

**Classes:**
- `class ERTProcessor` (10 methods)
  - `def __init__(self, mesh, electrode_positions, df)`
  - `def _log_init_stats(self)`
  - `def _route_parameters(self, params)`
  - `def _compute_paraDomain(self)`
  - `def _setup_manager(self, data, mgr_kwargs)`
  - `def _execute_inversion(self, inv_kwargs, routed_params)`
  - `def run_single(self, params)`
  - `def run_timelapse(self, params)`
  - `def run_ensemble(self, param_grid)`
  - `def save_results(self, folder_path, results_list, params)`

---

### `src\processing\inversion\pygimli_tools.py`

**Dependencies:**
- *Third-party:* `numpy, pandas, pygimli`

**Functions:**
- `def build_ert_container(df_survey, geom_df, err_values)` — *Converts a standardized Pandas DataFrame for a SINGLE survey into a PyGIMLi DataContainerERT.*
- `def build_ert_containers_timeseries(df, geom_df, err_values, date_col)` — *Wrapper that turns a multi-survey dataframe into a list of PyGIMLi containers. *
- `def get_common_configs(df, config_cols, date_col)` — *Identifies electrode configurations that exist across ALL surveys.*

---

### `src\visualization\basic_plotting.py`

**Dependencies:**
- *Third-party:* `matplotlib, numpy, pandas`

**Functions:**
- `def format_time_axis(ax)` — *Smart date locator with MM-dd format and 45-degree angle.*
- `def plot_sensors(df, ax, elec_numbers)` — *Plot selected electrodes on an existing axis.*
- `def plot_weather_data(weather_df, start_date, end_date, ax)`
- `def extract_polygons(mesh)` — *Directly builds Matplotlib polygons from a PyGIMLi mesh.*
- `def plot_array_on_mesh(polygons, array, ax)` — *Plot an array of values on a collection of polygons.*

---

### `src\visualization\inversion_data_report.py`

**Dependencies:**
- *Third-party:* `h5py, matplotlib, numpy, pandas, src`

**Classes:**
- `class InversionDataReport` (14 methods)
  - `def __init__(self, folder_path, elec_pos, results, mesh, paradomain, logs, filename)`
  - `def print(cls)`
  - `def print_absolute(cls, folder_path)`
  - `def print_relative(cls, folder_path, baseline_idx)`
  - `def build(self)`
  - `def build_absolute(self)`
  - `def build_relative(self, baseline_idx)`
  - `def _get_resistivity_norm(self, cmap_name, colors_per_interval)`
  - `def _get_relative_norm(self, cmap_name, vmin, vmax, step)`
  - `def _add_unified_colorbar(self, fig, cax, collection, title_prefix, ticks, labeled_ticks)`
  - `def _print_cover_page(self)`
  - `def _print_grid_pages(self, data_array, cmap_name, title_prefix, rows, cols, is_relative)`
  - `def _print_focus_layer(self, data_array, cmap_name, title_prefix, rows, is_relative)`
  - `def _print_convergence_page(self)`

---

### `src\visualization\raw_data_report.py`

**Dependencies:**
- *Third-party:* `pandas, src`

**Classes:**
- `class RawDataReport` (5 methods)
  - `def __init__(self, folder_path, df, elec_pos, max_groups, filename, station_id)`
  - `def print(cls)`
  - `def build(self)`
  - `def _print_cover_page(self)`
  - `def _build_timeseries_pages(self, plots_per_page)`

---

### `src\visualization\report_base.py`

**Dependencies:**
- *Third-party:* `matplotlib`

**Classes:**
- `class ReportBase` (5 methods)
  - `def __init__(self, filepath)`
  - `def __enter__(self)`
  - `def __exit__(self, exc_type, exc_val, exc_tb)`
  - `def page(self, rows, cols, height_ratios, width_ratios, landscape)`
  - `def build(self)`

---

### `src\visualization\single_filtrated_report.py`

**Dependencies:**
- *Third-party:* `matplotlib, numpy, pandas, scipy, src`

**Classes:**
- `class FiltratedDataReport` (6 methods)
  - `def __init__(self, folder_path, df_raw, df_clean, geom_df, mesh, preparator)`
  - `def print(cls, folder_path)`
  - `def compute_error_model(r_meas, err_rec, model_type)`
  - `def _plot_custom_pseudo(self, ax, df, val_col, title, cmap, pmin, pmax, log_scale, is_abs, custom_norm)`
  - `def _print_reciprocal_analysis_page(self)`
  - `def build(self)`

---

### `tests\loaders\00_test_all.py`

**Dependencies:**
- *Third-party:* `config, src, tests`

---

### `tests\loaders\test_elecs_projection.py`

**Dependencies:**
- *Third-party:* `config, matplotlib, src`

**Functions:**
- `def run_geometry_tests(paths, loader)`

---

### `tests\loaders\test_ert_loader.py`

**Dependencies:**
- *Third-party:* `config, src`

**Functions:**
- `def test_loading(site_id, file_path, load_function)` — *Test loading a single file using a specific loader method.*
- `def run_ert_loader_tests(paths)` — *Run full loader test suite for Berlier-Bergman and MCM sites.*

---

### `tests\loaders\test_header_scanner.py`

**Dependencies:**
- *Third-party:* `config, src`

**Functions:**
- `def run_header_tests(paths)`

---

### `tests\loaders\test_load_elecs_pos.py`

**Dependencies:**
- *Third-party:* `config, matplotlib, src`

**Functions:**
- `def run_geometry_tests(paths, loader)`

---

### `tests\loaders\test_sas4000_parser.py`

**Dependencies:**
- *Third-party:* `config, src`

**Functions:**
- `def run_sas4000_split_tests(paths, loader)`

---

### `tests\loaders\test_std_save_reload.py`

**Dependencies:**
- *Third-party:* `config, pandas, src`

**Functions:**
- `def run_save_reload_tests(paths, loader)`

---

### `tests\mesh\test_gmsh.py`

**Dependencies:**
- *Third-party:* `config, matplotlib, pygimli, src`

**Functions:**
- `def test_build_MCM_GEO_gmsh()`
- `def test_build_MCM_M2m_gmsh()`

---

### `tests\mesh\test_pygimli_mesh.py`

**Dependencies:**
- *Third-party:* `config, matplotlib, pygimli, src`

**Functions:**
- `def test_build_grid_mesh()`
- `def test_build_unstructured_mesh()`
- `def test_build_MCM_GEO()`
- `def test_build_MCM_M2m()`

---

### `tests\test.py`

**Dependencies:**
- *Third-party:* `numpy`

---

### `tests\visualization\test_plot_elec_geometry.py`

**Dependencies:**
- *Third-party:* `config, matplotlib, src`

**Functions:**
- `def test_loading(source, file_path, load_function)` — *Test loading a single file using a specific loader function.*

---

## 2. Cyclomatic Complexity Analysis (Radon)

> Scores: **A** (1-5, simple) to **F** (>41, extremely complex/bug-prone).

```text
code_diagnosis\architecture_audit.py
    F 16:0 analyze_python_file - C (19)
    F 86:0 build_full_audit - C (18)
    F 71:0 run_external_tool - B (6)
code_diagnosis\generate_architecture.py
    F 4:0 extract_signatures - C (11)
    F 35:0 generate_full_architecture - A (2)
code_diagnosis\generate_enhanced_architecture.py
    F 11:0 analyze_python_file - C (19)
    F 77:0 generate_deep_architecture_report - C (18)
code_diagnosis\generate_tree.py
    F 3:0 save_tree_to_file - A (2)
config\paths.py
    C 4:0 ProjectPaths - A (4)
    M 7:4 ProjectPaths.__init__ - A (3)
scripts\ERT_useful\clean_vec_pycache.py
    F 8:0 cleanup - B (7)
scripts\ERT_useful\prime_survey_building.py
    F 8:0 plot_pseudo_doi - A (4)
scripts\ERT_useful\prime_survey_building_V2.py
    F 8:0 plot_pseudo_doi - A (4)
scripts\MCM_GEO\GEO_data_filter.py
    F 10:0 filter_GEO - A (4)
scripts\MCM_GEO\GEO_gmsh.py
    F 18:0 build_gmsh_layered - B (7)
    F 164:0 build_MCM_GEO - A (3)
scripts\MCM_GEO\GEO_plot_report.py
    F 5:0 run_GEO - A (1)
scripts\MCM_GEO\GEO_single_survey_ensemble_inv.py
    F 10:0 run_GEO - A (1)
scripts\MCM_GEO\GEO_single_survey_inv.py
    F 10:0 run_GEO - A (1)
scripts\MCM_MONOS\MONO1M_single_survey_inv.py
    F 12:0 run_MONO1M - A (1)
scripts\MCM_MONOS\MONO1M_timelapse_inv.py
    F 12:0 run_TL_MONO1M - A (1)
scripts\MCM_MONOS\MONO2M_single_survey_inv.py
    F 13:0 run_MONO2M - A (1)
scripts\MCM_MONOS\MONO2M_timelapse_inv.py
    F 12:0 run_TL_MONO2M - A (1)
scripts\MCM_MONOS\MONOS_rawData_TLERT_report.py
    F 9:0 process_ert_site - A (5)
scripts\MCM_MONOS\plot_report.py
    F 5:0 run_plot_mono1m - A (1)
scripts\MCM_MONOS\mesh_building\MONO_gmsh.py
    F 18:0 build_gmsh_layered - B (7)
    F 164:0 test_build_MCM_M2m - A (2)
scripts\Weather\find_station.py
    F 3:0 get_stations_dict - B (9)
src\core\base.py
    M 92:4 ProjectBase.save - C (15)
    M 41:4 ProjectBase.load - C (13)
    M 86:4 ProjectBase._prepare_h5_value - B (8)
    C 20:0 ProjectBase - B (6)
    C 12:0 MemoryHandler - A (2)
    M 26:4 ProjectBase._setup_logging - A (2)
    M 13:4 MemoryHandler.__init__ - A (1)
    M 17:4 MemoryHandler.emit - A (1)
    M 21:4 ProjectBase.__init__ - A (1)
    M 71:4 ProjectBase.load_results - A (1)
    M 130:4 ProjectBase.save_mesh - A (1)
    M 136:4 ProjectBase.load_mesh - A (1)
src\loaders\ert_loader.py
    C 9:0 ERTLoader - B (7)
    M 50:4 ERTLoader._resolve_files - B (7)
    M 61:4 ERTLoader.finalize_standardization - B (7)
    M 114:4 ERTLoader.load_prime - B (7)
    M 157:4 ERTLoader.load_sas4000 - B (7)
    M 202:4 ERTLoader.load_ohmpi - B (6)
    M 12:4 ERTLoader.__init__ - A (3)
src\loaders\ert_loading_tools.py
    F 6:0 scan_header - B (10)
    F 259:0 load_geometry - B (8)
    F 89:0 get_reciprocal_mask - A (4)
    F 143:0 get_reciprocal_mask_vectorized - A (4)
    F 206:0 process_reciprocals - A (3)
    F 39:0 split_sas4000_surveys - A (2)
    F 58:0 pygimli_compute_geometric_factors - A (2)
    F 72:0 compute_geometric_factors - A (2)
src\loaders\weather_loading_tools.py
    F 5:0 fetch_weather_data - A (3)
src\mesh\gmesh_tools.py
    F 10:0 build_gmsh_mesh - A (4)
    F 122:0 build_gmsh_mono2m - A (4)
src\mesh\pygimli_mesh_tools.py
    F 113:0 build_mono2m_plc - C (12)
    F 15:0 build_unstructured_mesh - A (5)
    F 215:0 build_starting_model - A (5)
    F 93:0 safe_mesh_load - A (2)
    F 186:0 build_mono2m_meshes - A (2)
    F 9:0 build_grid_mesh - A (1)
    F 71:0 safe_mesh_save - A (1)
src\processing\data\data_preparator.py
    M 49:4 DataPreparator.filter_standard_survey - B (7)
    C 35:0 DataPreparator - A (4)
    M 103:4 DataPreparator.print_logs - A (3)
    F 8:0 log_filtration - A (1)
    M 36:4 DataPreparator.__init__ - A (1)
    M 43:4 DataPreparator.filter_mono2m_custom - A (1)
src\processing\data\data_tools.py
    F 32:0 interpolate_excluded_period - A (5)
    F 4:0 resample_timeseries - A (4)
    F 66:0 filter_common_measurements - A (4)
src\processing\data\filtration_tools.py
    F 4:0 get_date_range_mask - A (4)
    F 24:0 get_excluded_elecs_mask - A (2)
    F 33:0 get_excluded_configs_mask - A (2)
    F 19:0 get_threshold_mask - A (1)
    F 41:0 get_hampel_mask - A (1)
    F 57:0 get_discontinued_configs_mask - A (1)
src\processing\inversion\ert_processor.py
    M 100:4 ERTProcessor.save_results - C (14)
    M 23:4 ERTProcessor._route_parameters - B (6)
    C 11:0 ERTProcessor - A (4)
    M 87:4 ERTProcessor.run_ensemble - A (3)
    M 77:4 ERTProcessor.run_timelapse - A (2)
    M 12:4 ERTProcessor.__init__ - A (1)
    M 20:4 ERTProcessor._log_init_stats - A (1)
    M 47:4 ERTProcessor._compute_paraDomain - A (1)
    M 52:4 ERTProcessor._setup_manager - A (1)
    M 55:4 ERTProcessor._execute_inversion - A (1)
    M 71:4 ERTProcessor.run_single - A (1)
src\processing\inversion\pygimli_tools.py
    F 6:0 build_ert_container - C (12)
    F 72:0 get_common_configs - A (3)
    F 63:0 build_ert_containers_timeseries - A (2)
src\visualization\basic_plotting.py
    F 21:0 plot_sensors - A (5)
    F 47:0 plot_weather_data - A (4)
    F 95:0 extract_polygons - A (3)
    F 104:0 plot_array_on_mesh - A (3)
    F 8:0 format_time_axis - A (2)
src\visualization\inversion_data_report.py
    M 16:4 InversionDataReport.__init__ - C (17)
    M 200:4 InversionDataReport._print_grid_pages - C (11)
    M 236:4 InversionDataReport._print_focus_layer - B (8)
    M 273:4 InversionDataReport._print_convergence_page - B (6)
    C 15:0 InversionDataReport - A (5)
    M 86:4 InversionDataReport.build - A (3)
    M 99:4 InversionDataReport.build_absolute - A (3)
    M 107:4 InversionDataReport.build_relative - A (3)
    M 120:4 InversionDataReport._get_resistivity_norm - A (2)
    M 159:4 InversionDataReport._add_unified_colorbar - A (2)
    M 180:4 InversionDataReport._print_cover_page - A (2)
    M 72:4 InversionDataReport.print - A (1)
    M 77:4 InversionDataReport.print_absolute - A (1)
    M 82:4 InversionDataReport.print_relative - A (1)
    M 140:4 InversionDataReport._get_relative_norm - A (1)
src\visualization\raw_data_report.py
    M 53:4 RawDataReport._build_timeseries_pages - A (5)
    C 7:0 RawDataReport - A (3)
    M 8:4 RawDataReport.__init__ - A (1)
    M 30:4 RawDataReport.print - A (1)
    M 34:4 RawDataReport.build - A (1)
    M 38:4 RawDataReport._print_cover_page - A (1)
src\visualization\report_base.py
    C 9:0 ReportBase - A (3)
    M 19:4 ReportBase.__exit__ - A (3)
    M 29:4 ReportBase.page - A (3)
    M 10:4 ReportBase.__init__ - A (1)
    M 15:4 ReportBase.__enter__ - A (1)
    M 61:4 ReportBase.build - A (1)
src\visualization\single_filtrated_report.py
    M 169:4 FiltratedDataReport.build - C (19)
    M 49:4 FiltratedDataReport._plot_custom_pseudo - B (8)
    C 9:0 FiltratedDataReport - B (7)
    M 88:4 FiltratedDataReport._print_reciprocal_analysis_page - A (4)
    M 10:4 FiltratedDataReport.__init__ - A (3)
    M 31:4 FiltratedDataReport.compute_error_model - A (3)
    M 25:4 FiltratedDataReport.print - A (1)
tests\loaders\test_elecs_projection.py
    F 6:0 run_geometry_tests - A (4)
tests\loaders\test_ert_loader.py
    F 13:0 run_ert_loader_tests - A (2)
    F 5:0 test_loading - A (1)
tests\loaders\test_header_scanner.py
    F 4:0 run_header_tests - A (1)
tests\loaders\test_load_elecs_pos.py
    F 5:0 run_geometry_tests - A (2)
tests\loaders\test_sas4000_parser.py
    F 5:0 run_sas4000_split_tests - A (2)
tests\loaders\test_std_save_reload.py
    F 5:0 run_save_reload_tests - A (1)
tests\mesh\test_gmsh.py
    F 8:0 test_build_MCM_GEO_gmsh - A (1)
    F 25:0 test_build_MCM_M2m_gmsh - A (1)
tests\mesh\test_pygimli_mesh.py
    F 8:0 test_build_grid_mesh - A (1)
    F 13:0 test_build_unstructured_mesh - A (1)
    F 20:0 test_build_MCM_GEO - A (1)
    F 38:0 test_build_MCM_M2m - A (1)
tests\visualization\test_plot_elec_geometry.py
    F 6:0 test_loading - A (1)

147 blocks (classes, functions, methods) analyzed.
Average complexity: A (4.061224489795919)
```

---

## 3. Potential Dead Code & Unused Items (Vulture)

```text
config\paths.py:30: unused variable 'timestamp' (60% confidence)
config\paths.py:45: unused attribute 'TLERT_BB_SAS4000' (60% confidence)
config\paths.py:46: unused attribute 'TLERT_BB_OHMPI' (60% confidence)
config\paths.py:47: unused attribute 'TLERT_MCM_PRIME' (60% confidence)
config\paths.py:61: unused attribute 'MCM_MONO1M_ELECS_POS' (60% confidence)
scripts\MCM_GEO\GEO_gmsh.py:217: unused variable 'coll' (60% confidence)
scripts\MCM_MONOS\mesh_building\MONO_gmsh.py:191: unused variable 'coll' (60% confidence)
scripts\Weather\find_station.py:65: unused variable 'my_stations' (60% confidence)
src\core\base.py:71: unused method 'load_results' (60% confidence)
src\loaders\ert_loading_tools.py:58: unused function 'pygimli_compute_geometric_factors' (60% confidence)
src\loaders\ert_loading_tools.py:89: unused function 'get_reciprocal_mask' (60% confidence)
src\mesh\pygimli_mesh_tools.py:215: unused function 'build_starting_model' (60% confidence)
src\processing\data\data_preparator.py:42: unused method 'filter_mono2m_custom' (60% confidence)
src\processing\data\data_preparator.py:103: unused method 'print_logs' (60% confidence)
src\processing\data\data_tools.py:4: unused function 'resample_timeseries' (60% confidence)
src\processing\data\data_tools.py:32: unused function 'interpolate_excluded_period' (60% confidence)
src\processing\data\data_tools.py:66: unused function 'filter_common_measurements' (60% confidence)
src\processing\data\filtration_tools.py:4: unused function 'get_date_range_mask' (60% confidence)
src\processing\data\filtration_tools.py:24: unused function 'get_excluded_elecs_mask' (60% confidence)
src\processing\data\filtration_tools.py:33: unused function 'get_excluded_configs_mask' (60% confidence)
src\processing\data\filtration_tools.py:41: unused function 'get_hampel_mask' (60% confidence)
src\processing\data\filtration_tools.py:57: unused function 'get_discontinued_configs_mask' (60% confidence)
src\processing\inversion\pygimli_tools.py:72: unused function 'get_common_configs' (60% confidence)
src\visualization\basic_plotting.py:145: unused variable 'ymin' (60% confidence)
src\visualization\report_base.py:2: unused import 'matplotlib' (90% confidence)
src\visualization\report_base.py:19: unused variable 'exc_tb' (100% confidence)
tests\loaders\test_std_save_reload.py:17: unused variable 'df_reloaded' (60% confidence)
tests\mesh\test_gmsh.py:20: unused variable 'coll' (60% confidence)
tests\mesh\test_gmsh.py:46: unused variable 'coll' (60% confidence)
tests\mesh\test_pygimli_mesh.py:11: unused variable 'coll' (60% confidence)
tests\mesh\test_pygimli_mesh.py:18: unused variable 'coll' (60% confidence)
tests\mesh\test_pygimli_mesh.py:29: unused variable 'coll' (60% confidence)
tests\mesh\test_pygimli_mesh.py:46: unused variable 'coll' (60% confidence)
tests\mesh\test_pygimli_mesh.py:52: unused variable 'cb' (60% confidence)
```
