# Project Architecture: 02_Geophy_Processing

## Directory Tree & Signatures

```text
├── code_diagnosis
│   ├── architecture_audit.py
│   │       └── def analyze_python_file(file_path)
│   │           """Extracts imports, classes, and functions using AST."""
│   │       └── def run_external_tool(module_name, args)
│   │           """Runs a Python module tool using the current Python environment."""
│   │       └── def build_full_audit(target_dir, output_file, ignore_dirs)
│   ├── generate_architecture.py
│   │       └── def extract_signatures(file_path)
│   │           """Extracts top-level and class-level definitions from a Python file using AST."""
│   │       └── def generate_full_architecture(root_dir, output_file, ignore_dirs)
│   ├── generate_enhanced_architecture.py
│   │       └── def analyze_python_file(file_path)
│   │           """Parses a Python file to extract imports, class/method hierarchies, and functions."""
│   │       └── def generate_deep_architecture_report(root_dir, output_file, ignore_dirs)
│   └── generate_tree.py
│           └── def save_tree_to_file(root_dir, output_file, ignore_dirs)
├── config
│   └── paths.py
│           └── class ProjectPaths:
│               """Centralized, READ-ONLY path management for raw ERT data."""
│               └── def __init__(self, user, project_name)
├── scripts
│   ├── ERT_useful
│   │   ├── clean_vec_pycache.py
│   │   │       └── def cleanup(root)
│   │   ├── prime_survey_building.py
│   │   │       └── def plot_pseudo_doi(dataContainer, array_type)
│   │   │           """Plots the pseudo-section points for ERT data."""
│   │   └── prime_survey_building_V2.py
│   │           └── def plot_pseudo_doi(dataContainer, array_type)
│   │               """Plots the pseudo-section points for ERT data."""
│   ├── MCM_GEO
│   │   ├── GEO_data_filter.py
│   │   │       └── def filter_GEO(dd, sc, rec_err, plot_report)
│   │   ├── GEO_gmsh.py
│   │   │       └── def build_gmsh_layered(df, depth, interface_depth, extension, size_surface, size_interface, size_depth, params)
│   │   │           """Builds a 2D ERT mesh with a distinct structural interface (e.g., overburden vs tailings)"""
│   │   │       └── def build_MCM_GEO(show)
│   │   ├── GEO_plot_report.py
│   │   │       └── def run_GEO()
│   │   ├── GEO_single_survey_ensemble_inv.py
│   │   │       └── def run_GEO(dd, sc, rec_err)
│   │   └── GEO_single_survey_inv.py
│   │           └── def run_GEO()
│   ├── MCM_MONOS
│   │   ├── mesh_building
│   │   │   └── MONO_gmsh.py
│   │   │           └── def build_gmsh_layered(df, depth, interface_depth, extension, size_surface, size_interface, size_depth, params)
│   │   │               """Builds a 2D ERT mesh with a distinct structural interface (e.g., overburden vs tailings)"""
│   │   │           └── def test_build_MCM_M2m()
│   │   ├── MONO1M_single_survey_inv.py
│   │   │       └── def run_MONO1M()
│   │   ├── MONO1M_timelapse_inv.py
│   │   │       └── def run_TL_MONO1M()
│   │   ├── MONO2M_data_filter.py
│   │   ├── MONO2M_single_inv_flat_topo.py
│   │   ├── MONO2M_single_survey_inv.py
│   │   │       └── def run_MONO2M()
│   │   ├── MONO2M_timelapse_inv.py
│   │   │       └── def run_TL_MONO2M()
│   │   ├── MONOS_rawData_TLERT_report.py
│   │   │       └── def process_ert_site(site_id, geom_path, source_paths, offset_elec)
│   │   │           """Helper function to load geometry, parse PRIME data, and export the raw data report."""
│   │   ├── plot_report.py
│   │   │       └── def run_plot_mono1m()
│   │   └── run_both.py
│   └── Weather
│       ├── find_station.py
│       │       └── def get_stations_dict(province, search_term)
│       └── plot_weather.py
├── src
│   ├── core
│   │   ├── __init__.py
│   │   └── base.py
│   │           └── class MemoryHandler:
│   │               └── def __init__(self)
│   │               └── def emit(self, record)
│   │           └── class ProjectBase:
│   │               └── def __init__(self, memory)
│   │               └── def _setup_logging(self, memory)
│   │               └── def load(self, file_path)
│   │               └── def load_results(self, folder_path)
│   │               └── def _prepare_h5_value(self, key, val)
│   │               └── def save(self, data, file_path, metadata)
│   │               └── def save_mesh(self, mesh, file_path)
│   │               └── def load_mesh(self, file_path)
│   ├── loaders
│   │   ├── __init__.py
│   │   ├── ert_loader.py
│   │   │       └── class ERTLoader:
│   │   │           """Data loader for ERT instruments"""
│   │   │           └── def __init__(self, site_id, elec_pos)
│   │   │           └── def _resolve_files(self, source, pattern)
│   │   │           └── def finalize_standardization(self)
│   │   │           └── def load_prime(self, source, pattern, standardize, offset_elec)
│   │   │           └── def load_sas4000(self, source, pattern, standardize)
│   │   │           └── def load_ohmpi(self, source, pattern, standardize)
│   │   ├── ert_loading_tools.py
│   │   │       └── def scan_header(filepath, data_start_markers, delimiter, keys_to_keep)
│   │   │           """Scans a text file to extract specific metadata and find the data starting line."""
│   │   │       └── def split_sas4000_surveys(df, time_gap_hours)
│   │   │           """Detects multiple surveys within a single dataframe by looking for time """
│   │   │       └── def pygimli_compute_geometric_factors(df, df_elec_pos)
│   │   │           """Compute geometric factors using PyGIMLi."""
│   │   │       └── def compute_geometric_factors(df, df_elec_pos)
│   │   │           """Compute geometric factors using 3D Euclidean distances."""
│   │   │       └── def get_reciprocal_mask(df)
│   │   │           """Identify reciprocal ERT measurements by following acquisition order."""
│   │   │       └── def get_reciprocal_mask_vectorized(df)
│   │   │           """Identify reciprocal ERT measurements based on alternating occurrences"""
│   │   │       └── def process_reciprocals(df)
│   │   │           """Flips reciprocal dipoles to match forward configurations, isolates true """
│   │   │       └── def load_geometry(filepath, params)
│   │   │           """Load and process electrode geometry."""
│   │   └── weather_loading_tools.py
│   │           └── def fetch_weather_data(start_date, end_date, station_id, freq)
│   │               """Fetches daily weather data from Environment Canada and resamples to desired frequency."""
│   ├── mesh
│   │   ├── __init__.py
│   │   ├── gmesh_tools.py
│   │   │       └── def build_gmsh_mesh(df, depth, extension, size_surface, size_depth, params, out_path)
│   │   │           """Build an unstructured X-Z mesh using Gmsh tailored for PyGIMLi."""
│   │   │       └── def build_gmsh_mono2m(df, depth, extension, size_surface, size_depth, params)
│   │   └── pygimli_mesh_tools.py
│   │           └── def build_grid_mesh(x_min, x_max, y_min, y_max, dx, dy)
│   │               """Creates a structured quadrilateral grid."""
│   │           └── def build_unstructured_mesh(df, surface_offset, depth, extension, refine_dist)
│   │               """Create an unstructured triangular mesh from electrode positions with """
│   │           └── def safe_mesh_save(mesh, target_path)
│   │               """Saves a PyGIMLi mesh by bypassing Windows/C++ long path and accent limits."""
│   │           └── def safe_mesh_load(source_path)
│   │               """Loads a PyGIMLi mesh bypassing Windows/C++ encoding and path limits."""
│   │           └── def build_mono2m_plc(df, layer_depth, depth, extension, markers, area_top, area_bottom, curved_bottom)
│   │               """Helper: Builds the core layered polygons and fuses them with explicit area constraints."""
│   │           └── def build_mono2m_meshes(df, layer_depth, depth, extension, area_top, area_bottom, quality, add_boundary, bound_ext, bound_depth, start_markers)
│   │               """Builds both the inversion mesh and the starting model mesh simultaneously """
│   │           └── def build_starting_model(mesh, para_domain, rhomap, default_res)
│   │               """Maps resistivity values from a fine start mesh to the para_domain using a rhomap."""
│   ├── processing
│   │   ├── data
│   │   │   ├── __init__.py
│   │   │   ├── data_preparator.py
│   │   │   │       └── def log_filtration(func)
│   │   │   │           """Decorator to automatically log dropped measurements and top affected A-B pairs."""
│   │   │   │       └── class DataPreparator:
│   │   │   │           └── def __init__(self)
│   │   │   │           └── def filter_mono2m_custom(self, df, min_v, max_err)
│   │   │   │           └── def filter_standard_survey(self, df, thresholds)
│   │   │   │           └── def print_logs(self)
│   │   │   ├── data_tools.py
│   │   │   │       └── def resample_timeseries(df, freq_hours, max_gap_hours, timestamp_col, config_cols, meas_cols)
│   │   │   │           """Resamples data and interpolates missing values strictly bounded by max_gap_hours."""
│   │   │   │       └── def interpolate_excluded_period(df, electrodes, start_date, end_date, date_col, cols_to_interp, config_cols)
│   │   │   │           """Finds measurements containing specific electrodes during a time window, """
│   │   │   │       └── def filter_common_measurements(df, config_cols, date_col)
│   │   │   │           """Ensures every survey has the exact same length by keeping only the """
│   │   │   └── filtration_tools.py
│   │   │           └── def get_date_range_mask(df, start_date, end_date, return_df, date_col)
│   │   │               """Returns True for rows where the date is within the specified range."""
│   │   │           └── def get_threshold_mask(df, col, min_val, max_val)
│   │   │               """Returns True for values strictly within the min/max bounds."""
│   │   │           └── def get_excluded_elecs_mask(df, excluded_elecs, config_cols)
│   │   │               """Returns False if any electrode in the configuration is in the excluded list."""
│   │   │           └── def get_excluded_configs_mask(df, excluded_configs, config_cols)
│   │   │               """Returns False for exact A, B, M, N configuration matches."""
│   │   │           └── def get_hampel_mask(df, target_col, window_size, n_sigma, config_cols)
│   │   │               """Vectorized Hampel filter. Returns False for outliers detected within the rolling window."""
│   │   │           └── def get_discontinued_configs_mask(df, min_length, config_cols)
│   │   │               """Returns False for electrode configurations that have fewer total measurements than min_length."""
│   │   ├── inversion
│   │   │   ├── __init__.py
│   │   │   ├── ert_processor.py
│   │   │   │       └── class ERTProcessor:
│   │   │   │           └── def __init__(self, mesh, electrode_positions, df)
│   │   │   │           └── def _log_init_stats(self)
│   │   │   │           └── def _route_parameters(self, params)
│   │   │   │           └── def _compute_paraDomain(self)
│   │   │   │           └── def _setup_manager(self, data, mgr_kwargs)
│   │   │   │           └── def _execute_inversion(self, inv_kwargs, routed_params)
│   │   │   │           └── def run_single(self, params)
│   │   │   │           └── def run_timelapse(self, params)
│   │   │   │           └── def run_ensemble(self, param_grid)
│   │   │   │           └── def save_results(self, folder_path, results_list, params)
│   │   │   └── pygimli_tools.py
│   │   │           └── def build_ert_container(df_survey, geom_df, err_values)
│   │   │               """Converts a standardized Pandas DataFrame for a SINGLE survey into a PyGIMLi DataContainerERT."""
│   │   │           └── def build_ert_containers_timeseries(df, geom_df, err_values, date_col)
│   │   │               """Wrapper that turns a multi-survey dataframe into a list of PyGIMLi containers. """
│   │   │           └── def get_common_configs(df, config_cols, date_col)
│   │   │               """Identifies electrode configurations that exist across ALL surveys."""
│   │   └── __init__.py
│   ├── visualization
│   │   ├── basic_plotting.py
│   │   │       └── def format_time_axis(ax)
│   │   │           """Smart date locator with MM-dd format and 45-degree angle."""
│   │   │       └── def plot_sensors(df, ax, elec_numbers)
│   │   │           """Plot selected electrodes on an existing axis."""
│   │   │       └── def plot_weather_data(weather_df, start_date, end_date, ax)
│   │   │       └── def extract_polygons(mesh)
│   │   │           """Directly builds Matplotlib polygons from a PyGIMLi mesh."""
│   │   │       └── def plot_array_on_mesh(polygons, array, ax)
│   │   │           """Plot an array of values on a collection of polygons."""
│   │   ├── inversion_data_report.py
│   │   │       └── class InversionDataReport:
│   │   │           └── def __init__(self, folder_path, elec_pos, results, mesh, paradomain, logs, filename)
│   │   │           └── def print(cls)
│   │   │           └── def print_absolute(cls, folder_path)
│   │   │           └── def print_relative(cls, folder_path, baseline_idx)
│   │   │           └── def build(self)
│   │   │           └── def build_absolute(self)
│   │   │           └── def build_relative(self, baseline_idx)
│   │   │           └── def _get_resistivity_norm(self, cmap_name, colors_per_interval)
│   │   │           └── def _get_relative_norm(self, cmap_name, vmin, vmax, step)
│   │   │           └── def _add_unified_colorbar(self, fig, cax, collection, title_prefix, ticks, labeled_ticks)
│   │   │           └── def _print_cover_page(self)
│   │   │           └── def _print_grid_pages(self, data_array, cmap_name, title_prefix, rows, cols, is_relative)
│   │   │           └── def _print_focus_layer(self, data_array, cmap_name, title_prefix, rows, is_relative)
│   │   │           └── def _print_convergence_page(self)
│   │   ├── raw_data_report.py
│   │   │       └── class RawDataReport:
│   │   │           └── def __init__(self, folder_path, df, elec_pos, max_groups, filename, station_id)
│   │   │           └── def print(cls)
│   │   │           └── def build(self)
│   │   │           └── def _print_cover_page(self)
│   │   │           └── def _build_timeseries_pages(self, plots_per_page)
│   │   ├── report_base.py
│   │   │       └── class ReportBase:
│   │   │           └── def __init__(self, filepath)
│   │   │           └── def __enter__(self)
│   │   │           └── def __exit__(self, exc_type, exc_val, exc_tb)
│   │   │           └── def page(self, rows, cols, height_ratios, width_ratios, landscape)
│   │   │           └── def build(self)
│   │   └── single_filtrated_report.py
│   │           └── class FiltratedDataReport:
│   │               └── def __init__(self, folder_path, df_raw, df_clean, geom_df, mesh, preparator)
│   │               └── def print(cls, folder_path)
│   │               └── def compute_error_model(r_meas, err_rec, model_type)
│   │               └── def _plot_custom_pseudo(self, ax, df, val_col, title, cmap, pmin, pmax, log_scale, is_abs, custom_norm)
│   │               └── def _print_reciprocal_analysis_page(self)
│   │               └── def build(self)
│   └── __init__.py
├── tests
│   ├── loaders
│   │   ├── 00_test_all.py
│   │   ├── test_elecs_projection.py
│   │   │       └── def run_geometry_tests(paths, loader)
│   │   ├── test_ert_loader.py
│   │   │       └── def test_loading(site_id, file_path, load_function)
│   │   │           """Test loading a single file using a specific loader method."""
│   │   │       └── def run_ert_loader_tests(paths)
│   │   │           """Run full loader test suite for Berlier-Bergman and MCM sites."""
│   │   ├── test_header_scanner.py
│   │   │       └── def run_header_tests(paths)
│   │   ├── test_load_elecs_pos.py
│   │   │       └── def run_geometry_tests(paths, loader)
│   │   ├── test_sas4000_parser.py
│   │   │       └── def run_sas4000_split_tests(paths, loader)
│   │   └── test_std_save_reload.py
│   │           └── def run_save_reload_tests(paths, loader)
│   ├── mesh
│   │   ├── test_gmsh.py
│   │   │       └── def test_build_MCM_GEO_gmsh()
│   │   │       └── def test_build_MCM_M2m_gmsh()
│   │   └── test_pygimli_mesh.py
│   │           └── def test_build_grid_mesh()
│   │           └── def test_build_unstructured_mesh()
│   │           └── def test_build_MCM_GEO()
│   │           └── def test_build_MCM_M2m()
│   ├── visualization
│   │   └── test_plot_elec_geometry.py
│   │           └── def test_loading(source, file_path, load_function)
│   │               """Test loading a single file using a specific loader function."""
│   └── test.py
├── .env
├── ARCHITECTURE_AUDIT.md
├── JOURNAL.txt
├── main.py
├── README.md
└── TODO.txt
```
