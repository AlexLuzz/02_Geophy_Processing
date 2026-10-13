from matplotlib.colors import ListedColormap, BoundaryNorm
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import h5py
import json
import matplotlib.ticker as ticker

from src.visualization.report_base import ReportBase
from src.visualization.basic_plotting import extract_polygons, plot_array_on_mesh, plot_sensors

from src.mesh.pygimli_mesh_tools import safe_mesh_load 

class InversionDataReport(ReportBase):
    def __init__(self, folder_path: str | Path, elec_pos: pd.DataFrame, 
                 results=None, mesh=None, paradomain=None, logs: list = None,
                 filename: str = "_data_report.pdf"):
        
        folder_path = Path(folder_path)
        super().__init__(folder_path / filename)
        
        self.elec_pos = elec_pos
        self.logs = logs or []
        
        # --- OPTION A: Load everything from the standardized saved directory ---
        if results is None:
            self.mesh = safe_mesh_load(str(folder_path / "forward_mesh.bms"))
            self.paradomain = safe_mesh_load(str(folder_path / "paradomain.bms"))
            
            with open(folder_path / "params.json", 'r') as f:
                config = json.load(f)
            
            with h5py.File(folder_path / "results.h5", 'r') as f:
                self.models = f['models'][()]
                self.responses = f['responses'][()]
                self.times = [s.decode('utf-8') if isinstance(s, bytes) else s for s in f['times'][()]]
                
                chi2_hist_pad = f['chi2_history'][()]
                self.chi2_histories = [h[~np.isnan(h)] for h in chi2_hist_pad] # Clean NaNs
                
            self.rrms = config.get('rrms', [0]*len(self.times))
            self.chi2 = config.get('chi2', [0]*len(self.times))
            self.params = config.get('run_params', [{} for _ in self.times])
            
            sm = config.get('start_model')
            self.start_model = np.array(sm) if sm is not None else None

        # --- OPTION B: Load directly from memory (e.g. straight out of ERTProcessor) ---
        else:
            self.mesh = mesh
            self.paradomain = paradomain
            
            if isinstance(results, dict):
                results = [results]
                
            self.models = np.array([r['model'] for r in results])
            self.responses = np.array([r['response'] for r in results])
            self.times = [r.get('date_survey', r.get('time', 'static')) for r in results]
            
            self.rrms = np.array([r.get('rrms', r.get('rms', 0)) for r in results], dtype=float)
            self.chi2 = np.array([r.get('chi2', 0) for r in results], dtype=float)
            self.params = [r.get('params', {}) for r in results]
            self.chi2_histories = [r.get('chi2_history', []) for r in results]
            
            self.start_model = results[0].get('start_model') if len(results) > 0 else None

        self.mesh_polygons = extract_polygons(self.mesh)
        self.paradomain_polygons = extract_polygons(self.paradomain)

    @classmethod
    def print(cls, *args, **kwargs):
        with cls(*args, **kwargs) as report:
            report.build()

    @classmethod
    def print_absolute(cls, folder_path, *args, **kwargs):
        with cls(folder_path, filename="_absolute_report.pdf", *args, **kwargs) as report:
            report.build_absolute()

    @classmethod
    def print_relative(cls, folder_path, baseline_idx=0, *args, **kwargs):
        with cls(folder_path, filename="_relative_report.pdf", *args, **kwargs) as report:
            report.build_relative(baseline_idx)

    def build(self):
        self._print_cover_page()
        if len(self.models) > 0:
            
            cmap_name = 'Spectral_r'
            title_prefix = "Resistivity (Ohm·m)"

            self._print_grid_pages(self.models, cmap_name=cmap_name, title_prefix=title_prefix)
            self._print_focus_layer(self.models, cmap_name=cmap_name, title_prefix=title_prefix, rows=4)
            
        if len(self.chi2_histories) > 0:
            self._print_convergence_page()

    def build_absolute(self):
        self._print_cover_page()
        if len(self.models) > 0:
            self._print_grid_pages(self.models, cmap_name='Spectral_r', title_prefix="Resistivity (Ohm·m)", is_relative=False)
            self._print_focus_layer(self.models, cmap_name='Spectral_r', title_prefix="Resistivity (Ohm·m)", rows=4, is_relative=False)
        if len(self.chi2_histories) > 0:
            self._print_convergence_page()

    def build_relative(self, baseline_idx=0):
        self._print_cover_page()
        if len(self.models) > 0:
            # Compute the mathematical variation upfront
            baseline = self.models[baseline_idx]
            rel_models = ((self.models - baseline) / baseline) * 100
            
            self._print_grid_pages(rel_models, cmap_name='RdBu_r', title_prefix="Relative Variation (%)", is_relative=True)
            self._print_focus_layer(rel_models, cmap_name='RdBu_r', title_prefix="Relative Variation (%)", rows=4, is_relative=True)
            
        if len(self.chi2_histories) > 0:
            self._print_convergence_page()

    def _get_resistivity_norm(self, cmap_name, colors_per_interval=2):
        # Your fixed values that will actually receive text labels
        labeled_ticks = [#0.5, 1, 2, 
                         5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000]
        
        boundaries = []
        # Generate exact intermediate boundaries based on the number of colors you want
        for i in range(len(labeled_ticks) - 1):
            steps = np.geomspace(labeled_ticks[i], labeled_ticks[i+1], colors_per_interval + 1)
            boundaries.extend(steps[:-1])
            
        boundaries.append(labeled_ticks[-1])
        boundaries = np.array(boundaries)

        cmap = plt.colormaps[cmap_name].resampled(len(boundaries) - 1).copy()
        cmap.set_under("gray")
        cmap.set_over("black")

        return cmap, BoundaryNorm(boundaries, cmap.N), boundaries, labeled_ticks

    def _get_relative_norm(self, cmap_name='RdBu_r', vmin=-30, vmax=30, step=5):
        """Creates a symmetric diverging colormap with a strict white center."""
        boundaries = np.arange(vmin, vmax + step, step)
        labeled_ticks = boundaries
        
        base_cmap = plt.colormaps[cmap_name].resampled(len(boundaries) - 1)
        colors = base_cmap(np.linspace(0, 1, base_cmap.N))
        
        # Force the two central color bins to be pure white (RGBA)
        mid_idx = len(colors) // 2
        colors[mid_idx] = [1.0, 1.0, 1.0, 1.0]      # The step right of zero
        colors[mid_idx - 1] = [1.0, 1.0, 1.0, 1.0]  # The step left of zero
        
        cmap = ListedColormap(colors)
        cmap.set_under("navy")
        cmap.set_over("darkred")
        
        return cmap, BoundaryNorm(boundaries, cmap.N), boundaries, labeled_ticks

    def _add_unified_colorbar(self, fig, cax, collection, title_prefix, ticks=None, labeled_ticks=None):
        # Pass all boundaries to 'ticks' so every color limit gets a physical tick mark
        cbar = fig.colorbar(collection, cax=cax, orientation='vertical', spacing='uniform', ticks=ticks, extend='both')
        
        if labeled_ticks is not None:
            # Only print the number if it matches a value in our labeled_ticks list
            def format_tick(x, pos):
                # np.isclose prevents floating point mismatch errors
                if any(np.isclose(x, lt) for lt in labeled_ticks):
                    return f"{x:g}" # Format 'g' elegantly handles 0.5 without truncating it to 0
                return ""
            
            cbar.ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_tick))
            
        cbar.set_label(title_prefix, fontsize=10)
        cbar.ax.tick_params(labelsize=8)
        
        # Ensure Matplotlib doesn't auto-generate its own background ticks
        cbar.ax.minorticks_off() 
        return cbar

    def _print_cover_page(self):
        with self.page(rows=4, cols=1) as (fig, gs):
            # Title fully removed.
            
            ax_logs = fig.add_subplot(gs[0, 0])
            ax_logs.axis('off')
            log_text = "\n".join(self.logs) if self.logs else "No execution logs provided."
            ax_logs.text(0.02, 0.95, log_text, fontsize=9, fontfamily='monospace', va='top', ha='left', wrap=True)

            ax_mesh = fig.add_subplot(gs[1, 0])
            plot_array_on_mesh(self.mesh_polygons, ax=ax_mesh, edgecolor='black', alpha=0.3, linewidth=0.1)
            plot_sensors(self.elec_pos, ax=ax_mesh, show_numbers=True, number_every=4)
            ax_mesh.set_title(f"Forward Mesh: {self.mesh.cellCount()} cells, {self.mesh.nodeCount()} nodes", fontsize=8)
            ax_mesh.set_ylim([self.mesh.yMin(), self.mesh.yMax() + 6])

            ax_pd = fig.add_subplot(gs[2, 0])
            plot_array_on_mesh(self.paradomain_polygons, self.start_model, ax=ax_pd, edgecolor='black', alpha=0.3, linewidth=0.1)
            ax_pd.set_title(f"Starting Model on Paradomain: {self.paradomain.cellCount()} cells", fontsize=8)
            ax_pd.set_ylim([self.paradomain.yMin(), self.paradomain.yMax() + 6])

    def _print_grid_pages(self, data_array: np.ndarray, cmap_name: str, title_prefix: str, 
                          rows: int = 4, cols: int = 2, is_relative: bool = False):
        
        if is_relative:
            cmap, norm, all_ticks, labeled_ticks = self._get_relative_norm(cmap_name)
        else:
            cmap, norm, all_ticks, labeled_ticks = self._get_resistivity_norm(cmap_name)

        plots_per_page = rows * cols
        n_plots = len(data_array)
        chunks = [range(i, min(i + plots_per_page, n_plots)) for i in range(0, n_plots, plots_per_page)]

        for chunk in chunks:
            with self.page(rows=rows, cols=cols + 1, width_ratios=[1, 1, 0.05], landscape=True) as (fig, gs):
                for plot_idx, i in enumerate(chunk):
                    r, c = divmod(plot_idx, cols)
                    ax = fig.add_subplot(gs[r, c])
                    ax, collection = plot_array_on_mesh(self.paradomain_polygons, array=data_array[i], ax=ax, cmap=cmap, norm=norm)
                    plot_sensors(self.elec_pos, ax=ax)

                    time_str = str(self.times[i])
                    param_str = " | ".join([f"{k}: {v}" for k, v in self.params[i].items()]) if self.params[i] else ""
                    metrics_str = f"RRMS: {self.rrms[i]:.1f}% (\u03C7\u00B2: {self.chi2[i]:.1f})"
                    left_title = f"[{param_str}]\n{metrics_str}" if param_str else metrics_str

                    ax.set_title(left_title, fontsize=9, loc='left', pad=4)
                    ax.set_title(time_str, fontsize=9, loc='right', color='dimgrey')
                    ax.tick_params(labelsize=8)
                    
                    if c == 0: ax.set_ylabel("Z (m)", fontsize=8)
                    if r == rows - 1 or plot_idx >= len(chunk) - cols: ax.set_xlabel("X (m)", fontsize=8)

                cbar_ax = fig.add_subplot(gs[1:3, -1])
                self._add_unified_colorbar(fig, cbar_ax, collection, title_prefix, 
                                           ticks=all_ticks, labeled_ticks=labeled_ticks)

    def _print_focus_layer(self, data_array: np.ndarray, cmap_name: str, title_prefix: str, 
                           rows: int = 4, is_relative: bool = False):
        
        if is_relative:
            cmap, norm, all_ticks, labeled_ticks = self._get_relative_norm(cmap_name)
        else:
            cmap, norm, all_ticks, labeled_ticks = self._get_resistivity_norm(cmap_name)

        for start in range(0, len(data_array), rows):
            with self.page(rows=rows, cols=4, width_ratios=[1, 0.35, 0.35, 0.05], landscape=True) as (fig, gs):
                for row in range(min(rows, len(data_array) - start)):
                    i = start + row

                    ax = fig.add_subplot(gs[row, 0])
                    ax, collection = plot_array_on_mesh(self.paradomain_polygons, array=data_array[i], ax=ax, cmap=cmap, norm=norm)
                    plot_sensors(self.elec_pos, ax=ax)

                    time_str = str(self.times[i])
                    param_str = " | ".join(f"{k}: {v}" for k, v in self.params[i].items())
                    metrics_str = f"RRMS: {self.rrms[i]:.1f}% (χ²: {self.chi2[i]:.1f})"

                    ax.set_title(f"[{param_str}]\n{metrics_str}" if param_str else metrics_str, fontsize=9, loc="left", pad=4)
                    ax.set_title(time_str, fontsize=9, loc="right", color="dimgrey")
                    ax.set_ylabel("Z (m)", fontsize=8)

                    for col, xlim, ylim in [(1, (50, 75), (-8, 2)), (2, (150, 175), (-15, -5))]:
                        ax_zoom = fig.add_subplot(gs[row, col])
                        ax_zoom, _ = plot_array_on_mesh(self.paradomain_polygons, array=data_array[i], ax=ax_zoom, cmap=cmap, norm=norm)
                        ax_zoom.set(xlim=xlim, ylim=ylim)
                        plot_sensors(self.elec_pos, ax=ax_zoom)

                    if row == rows - 1:
                        ax.set_xlabel("X (m)", fontsize=8)

                cbar_ax = fig.add_subplot(gs[1:3, -1])
                self._add_unified_colorbar(fig, cbar_ax, collection, title_prefix, ticks=all_ticks, labeled_ticks=labeled_ticks)

    def _print_convergence_page(self):
        with self.page(rows=1, cols=1, landscape=True) as (fig, gs):
            ax = fig.add_subplot(gs[0, 0])

            for hist, param, time in zip(self.chi2_histories, self.params, self.times):
                if np.isfinite(hist).any():
                    label = ", ".join(f"{k}:{v}" for k, v in param.items()) if param else str(time)
                    ax.plot(np.arange(1, len(hist) + 1), hist, "o-", ms=4, lw=1.5, label=label)

            ax.set(xlabel="Iteration Number", ylabel="χ² (Chi-Square Misfit")
            ax.set_yscale("log")
            ax.grid(True, which="both", ls="--", alpha=.5)
            if ax.lines:
                ax.legend(title="Run Identifiers", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
                fig.subplots_adjust(right=.75)