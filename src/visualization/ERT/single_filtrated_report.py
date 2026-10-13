import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize, BoundaryNorm
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.optimize import curve_fit
from src.visualization.report_base import ReportBase

class FiltratedDataReport(ReportBase):
    def __init__(self, folder_path: str | Path, df_raw: pd.DataFrame, df_clean: pd.DataFrame, geom_df: pd.DataFrame, mesh=None, preparator=None):
        filepath = Path(folder_path) / "filtrated_data_report.pdf"
        super().__init__(filepath)
        
        self.df_raw = df_raw
        self.df_clean = df_clean
        self.geom_df = geom_df
        
        self.logs = []
        if preparator and getattr(preparator, 'memory_handler', None):
            self.logs = preparator.memory_handler.logs
        
        self.df_dropped = df_raw.loc[~df_raw.index.isin(df_clean.index)].copy()

    @classmethod
    def print(cls, folder_path: str | Path, *args, **kwargs):
        with cls(folder_path, *args, **kwargs) as report:
            report.build()
            return report

    @staticmethod
    def compute_error_model(r_meas: np.ndarray, err_rec: np.ndarray, model_type: str = 'power') -> dict:
        """Computes error model parameters from reciprocal measurements."""
        if model_type == 'power':
            def power_law(x, a, b, c):
                return a * (x ** b) + c
            
            popt, _ = curve_fit(power_law, r_meas, err_rec, p0=[0.05, 1.0, 0.001])
            return {'model_type': 'power', 'a': popt[0], 'b': popt[1], 'c': popt[2]}
            
        elif model_type == 'linear':
            def linear_law(x, a, b):
                return a * x + b
                
            popt, _ = curve_fit(linear_law, r_meas, err_rec, p0=[0.05, 0.001])
            return {'model_type': 'linear', 'a': popt[0], 'b': popt[1]}
            
        raise ValueError(f"Unknown model_type: {model_type}")

    def _plot_custom_pseudo(self, ax, df, val_col, title, cmap, pmin=3, pmax=97, log_scale=True, is_abs=False, custom_norm=None):
        if df.empty or val_col not in df.columns or df[val_col].isna().all():
            ax.text(0.5, 0.5, f"No Data for {val_col}", ha='center', va='center', fontsize=10)
            ax.axis('off')
            return None
            
        pos = self.geom_df.set_index('elec_number')['X']
        df_valid = df.dropna(subset=['A', 'B', 'M', 'N', val_col])
        
        x_A, x_B = pos.loc[df_valid['A']].values, pos.loc[df_valid['B']].values
        x_M, x_N = pos.loc[df_valid['M']].values, pos.loc[df_valid['N']].values
        
        # Calculate array center and empirical pseudo-depth
        x_AB, x_MN = (x_A + x_B) / 2, (x_M + x_N) / 2
        x_plot = (x_AB + x_MN) / 2
        z_plot = -np.abs(x_AB - x_MN) / 3 
        
        vals = df_valid[val_col].values
        if is_abs:
            vals = np.abs(vals)
            
        # Prioritize custom_norm if provided
        if custom_norm is not None:
            norm = custom_norm
        else:
            vmin, vmax = np.percentile(vals, [pmin, pmax]) if len(vals) > 0 else (0.1, 1)
            if log_scale:
                vmin = max(vmin, 1e-4) # Prevent log(0)
                norm = LogNorm(vmin=vmin, vmax=max(vmax, vmin + 1e-4))
            else:
                norm = Normalize(vmin=vmin, vmax=vmax)
            
        sc = ax.scatter(x_plot, z_plot, c=vals, cmap=cmap, norm=norm, s=15, marker='s', edgecolors='none')
        ax.set_title(title, fontsize=10, loc='left', pad=3)
        ax.set_xlabel("X (m)", fontsize=8)
        ax.set_ylabel("Pseudo-Depth", fontsize=8)
        ax.tick_params(labelsize=7)
        return sc

    def _print_reciprocal_analysis_page(self):
        if 'reciprocal' not in self.df_raw.columns or not self.df_raw['reciprocal'].any():
            return 

        df_fwd = self.df_clean[self.df_clean['reciprocal'] == False].copy()
        df_rec = self.df_clean[self.df_clean['reciprocal'] == True].copy()

        df_pair = df_fwd.merge(
            df_rec,
            on=['A', 'B', 'M', 'N'],
            suffixes=('_fwd', '_rec'),
            how='inner'
        )
            
        if df_pair.empty:
            return

        r_forward = df_pair['R (Ohm)_fwd'].to_numpy()
        r_recip = df_pair['R (Ohm)_rec'].to_numpy()
        
        r_mean = (r_forward + r_recip) / 2
        delta_r_abs = np.abs((r_forward - r_recip) / 2)
        err_rel = delta_r_abs / r_mean 

        with self.page(rows=3, cols=1, landscape=False, height_ratios=[2, 1, 1]) as (fig, gs):
            fig.suptitle("Reciprocal Error Analysis & Error Models", fontsize=14, fontweight='bold', y=0.95)

            ax1 = fig.add_subplot(gs[0, 0])
            ax1.scatter(r_forward, r_recip, alpha=0.5, s=10, edgecolor='none')
            
            min_val = min(np.min(r_forward), np.min(r_recip))
            max_val = max(np.max(r_forward), np.max(r_recip))
            lim_min, lim_max = min_val * 0.8, max_val * 1.2
            
            ax1.plot([lim_min, lim_max], [lim_min, lim_max], 'k--', alpha=0.7, label='1:1')
            ax1.set_xlim(lim_min, lim_max)
            ax1.set_ylim(lim_min, lim_max)
            ax1.set_xscale('log')
            ax1.set_yscale('log')
            ax1.set_xlabel(r"$R_{forward}$ ($\Omega$)")
            ax1.set_ylabel(r"$R_{reciprocal}$ ($\Omega$)")
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            lin_model = self.compute_error_model(r_mean, err_rel, 'linear')
            pow_model = self.compute_error_model(r_mean, err_rel, 'power')
            r_plot = np.logspace(np.log10(r_mean.min()), np.log10(r_mean.max()), 100)

            ax2 = fig.add_subplot(gs[1, 0])
            ax2.scatter(r_mean, err_rel, alpha=0.4, s=8, c='tab:blue')
            ax2.plot(r_plot, lin_model['a'] * r_plot + lin_model['b'], 'r-', linewidth=2, 
                     label=f"$\Delta R/R = {lin_model['a']:.3f}R + {lin_model['b']:.3f}$")
            ax2.set_xlabel(r"$R$ ($\Omega$)")
            ax2.set_ylabel(r"$\Delta R / R$")
            ax2.set_xscale('log')
            ax2.set_yscale('log')
            ax2.legend()
            ax2.grid(True, alpha=0.3)

            ax3 = fig.add_subplot(gs[2, 0])
            ax3.scatter(r_mean, err_rel, alpha=0.4, s=8, c='tab:green')
            mod_r = pow_model['a'] * (r_plot ** pow_model['b']) + pow_model['c']
            ax3.plot(r_plot, mod_r, 'r-', linewidth=2, 
                     label=f"$\Delta R/R = {pow_model['a']:.3f}R^{{{pow_model['b']:.3f}}} + {pow_model['c']:.3f}$")
            ax3.set_xlabel(r"$R$ ($\Omega$)")
            ax3.set_ylabel(r"$\Delta R / R$")
            ax3.set_xscale('log')
            ax3.set_yscale('log')
            ax3.legend()
            ax3.grid(True, alpha=0.3)

            fig.tight_layout(rect=[0, 0.03, 1, 0.9])

        # Apply model across full clean dataframe
        df_clean_r = self.df_clean['R (Ohm)'].to_numpy()
        # power model
        mod_r_full = pow_model['a'] * (df_clean_r ** pow_model['b']) + pow_model['c']
        # linear model
        #mod_r_full = pow_model['a'] * (df_clean_r ** pow_model['b']) + pow_model['c']
        self.df_clean['err_val (%)'] = np.abs(mod_r_full * 100)

    def build(self):
        # --- PAGE 1: Filtration Logs ---
        with self.page(rows=1, cols=1, landscape=False) as (fig, gs):
            fig.suptitle("DataPreparator | Filtration Log Summary", fontsize=14, fontweight='bold', y=0.98)
            ax = fig.add_subplot(gs[0, 0])
            ax.axis('off')
            
            if self.logs:
                clean_logs = [log.split(" - ")[-1] if " - " in log else log for log in self.logs]
                log_text = "\n\n".join(clean_logs)
            else:
                log_text = "No in-memory logs found."
            ax.text(0.05, 0.95, log_text, fontsize=10, family='monospace', va='top', wrap=True)

        # --- PAGE 2: Raw Diagnostics ---
        with self.page(rows=4, cols=1, landscape=False, height_ratios=[1, 1, 1, 1]) as (fig, gs):
            
            # --- Block 1: Injected Current ---
            ticks_I = [1, 2, 5, 20, 50, 100]
            cmap_I = plt.cm.get_cmap('viridis', len(ticks_I) - 1)
            norm_I = BoundaryNorm(ticks_I, cmap_I.N)
            
            ax1 = fig.add_subplot(gs[1, 0])
            sc1 = self._plot_custom_pseudo(ax1, self.df_raw, 'Iab (mA)', "Injected Current (Iab)", cmap_I, custom_norm=norm_I)
            if sc1:
                cbar = fig.colorbar(sc1, ax=ax1, pad=0.01, fraction=0.03, spacing='uniform', ticks=ticks_I)
                cbar.ax.set_yticklabels([str(t) for t in ticks_I])
                cbar.set_label("mA", fontsize=8)
            
            # --- Block 2: Measured Voltage ---
            ticks_V = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10, 50, 100]
            cmap_V = plt.cm.get_cmap('plasma', len(ticks_V) - 1)
            norm_V = BoundaryNorm(ticks_V, cmap_V.N)
            
            ax2 = fig.add_subplot(gs[2, 0])
            sc2 = self._plot_custom_pseudo(ax2, self.df_raw, 'Vmn (mV)', "Measured Voltage (|Vmn|)", cmap_V, is_abs=True, custom_norm=norm_V)
            if sc2: 
                cbar = fig.colorbar(sc2, ax=ax2, pad=0.01, fraction=0.03, spacing='uniform', ticks=ticks_V)
                cbar.ax.set_yticklabels([str(t) for t in ticks_V])
                cbar.set_label("|mV|", fontsize=8)
            
            # --- Block 3: Errors ---
            ticks_E = [0.1, 0.5, 1, 2, 5, 10, 20, 50, 100]
            cmap_E = plt.cm.get_cmap('inferno', len(ticks_E) - 1)
            norm_E = BoundaryNorm(ticks_E, cmap_E.N)
            
            ax3 = fig.add_subplot(gs[3, 0])
            if 'err_rec (%)' in self.df_raw.columns and self.df_raw['err_rec (%)'].notna().any():
                sc3 = self._plot_custom_pseudo(ax3, self.df_raw, 'err_rec (%)', "Reciprocal Error (%)", cmap_E, custom_norm=norm_E)
            else:
                sc3 = self._plot_custom_pseudo(ax3, self.df_raw, 'err_stk (%)', "Stacking Error (%)", cmap_E, custom_norm=norm_E)
                
            if sc3: 
                cbar = fig.colorbar(sc3, ax=ax3, pad=0.01, fraction=0.03, spacing='uniform', ticks=ticks_E)
                cbar.ax.set_yticklabels([str(t) for t in ticks_E])
                cbar.set_label("%", fontsize=8)
                
        # --- PAGE 3: Apparent Resistivity Filtration ---
        with self.page(rows=3, cols=1, landscape=False) as (fig, gs):
            fig.suptitle(f"Filtration Map | Dropped {len(self.df_dropped)}/{len(self.df_raw)}", fontsize=12, fontweight='bold', y=0.98)
            
            ax0 = fig.add_subplot(gs[0, 0])
            sc_raw = self._plot_custom_pseudo(ax0, self.df_raw, 'rhoa (Ohm.m)', "RAW Apparent Resistivity", 'Spectral_r', is_abs=True)
            shared_norm = sc_raw.norm if sc_raw else None
            
            ax1 = fig.add_subplot(gs[1, 0])
            self._plot_custom_pseudo(ax1, self.df_clean, 'rhoa (Ohm.m)', "CLEAN Apparent Resistivity", 'Spectral_r', is_abs=True)
            if sc_raw and ax1.collections: ax1.collections[0].set_norm(shared_norm)
            
            ax2 = fig.add_subplot(gs[2, 0])
            if not self.df_dropped.empty:
                self._plot_custom_pseudo(ax2, self.df_dropped, 'rhoa (Ohm.m)', "DROPPED Measurements", 'Spectral_r', is_abs=True)
                if sc_raw and ax2.collections: ax2.collections[0].set_norm(shared_norm)
            else:
                ax2.text(0.5, 0.5, "No Data Dropped", ha='center', va='center')
                ax2.axis('off')
                
            if sc_raw:
                cbar = fig.colorbar(sc_raw, ax=[ax0, ax1, ax2], orientation='vertical', fraction=0.03, pad=0.02)
                cbar.set_label(r"Absolute $\rho_a$ ($\Omega\cdot$m)", fontsize=10)

        # --- PAGE 4: Error Models ---
        self._print_reciprocal_analysis_page()