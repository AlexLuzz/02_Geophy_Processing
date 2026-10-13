import pandas as pd
from pathlib import Path
from src.visualization.report_base import ReportBase
from src.visualization.basic_plotting import format_time_axis, plot_sensors
from src.loaders.weather_loading_tools import fetch_weather_data

class RawDataReport(ReportBase):
    def __init__(self, folder_path: str | Path, df: pd.DataFrame, elec_pos: pd.DataFrame, 
                 max_groups: int = 300, 
                 filename: str = "_raw_data_report.pdf",
                 station_id: int = 30172):
        
        # 1. Enforce strict, standardized static output filename
        folder_path = Path(folder_path)
        super().__init__(folder_path / filename)
        
        self.df = df.copy()
        self.elec_pos = elec_pos
        self.max_groups = max_groups

        # Ensure datetime formatting and chronological sorting
        self.df['date_meas'] = pd.to_datetime(self.df['date_meas'])
        self.df = self.df.sort_values(by='date_meas')
        self.start, self.end = self.df['date_meas'].min(), self.df['date_meas'].max()

        # Fetch environmental data for the survey period
        self.weather_df = fetch_weather_data(self.start, self.end, station_id)

    @classmethod
    def print(cls, *args, **kwargs):
        with cls(*args, **kwargs) as report:
            report.build()

    def build(self):
        self._print_cover_page()
        self._build_timeseries_pages()

    def _print_cover_page(self):
        with self.page() as (fig, gs):
            ax = fig.add_subplot(gs[0, 0])
            ax.axis('off')
            
            # Formatted log text displaying basic dataset characteristics
            log_text = (
                f"RAW DATASET LOG\n"
                f"{'='*30}\n"
                f"Total Measurements: {len(self.df)} rows\n"
                f"Date Range: {self.start.date()} to {self.end.date()}\n\n"
                f"Preview:\n{self.df.head(10).to_string()}"
            )
            ax.text(0.05, 0.95, log_text, transform=ax.transAxes, fontsize=8, family='monospace', va='top')

    def _build_timeseries_pages(self, plots_per_page=4):
        col = 'rhoa (Ohm.m)'
        grouped = list(
            self.df.groupby(['A', 'B', 'M', 'N'], sort=False)
        )[:self.max_groups]

        for i in range(0, len(grouped), plots_per_page):
            chunk = grouped[i:i + plots_per_page]

            with self.page(
                rows=plots_per_page + 1, cols=2,
                width_ratios=[3, 1], landscape=True
            ) as (fig, gs):

                # Add a single shared Y-axis label in the middle of the page height
                # Adjust the x-coordinate (0.04) if it overlaps with your left margin
                fig.text(0.01, 0.5, "Apparent resistivity ($\Omega\cdot$m)", va='center', rotation='vertical', fontsize=10)

                for j, ((a, b, m, n), g) in enumerate(chunk):
                    ax = fig.add_subplot(gs[j, 0])
                    ax_geom = fig.add_subplot(gs[j, 1])

                    # --- Timeseries ---
                    ax.plot(g['date_survey'], g[col], 'o-', color='tab:blue',
                            ms=3, lw=1, alpha=.7)

                    r = g[g['reciprocal'] == True]
                    ax.scatter(r['date_survey'], r[col], color='red', s=20, zorder=3)

                    ax.grid(True, ls='--', alpha=.5)
                    
                    # Force X-axis limits to match the global dataset timeframe
                    ax.set_xlim(self.start, self.end)
                    
                    # Hide the X-axis tick labels for the resistivity plots
                    ax.tick_params(labelbottom=False) 

                    # --- Geometry ---
                    plot_sensors(self.elec_pos, ax=ax_geom)
                    plot_sensors(self.elec_pos.iloc[[a - 1, b - 1]],
                                    ax=ax_geom, color='red')
                    plot_sensors(self.elec_pos.iloc[[m - 1, n - 1]],
                                    ax=ax_geom, color='blue')
                    
                    # Add electrode configuration text rectangle
                    config_text = f"A-B-M-N : {a}-{b}-{m}-{n}"
                    ax_geom.text(0.3, 0.15, config_text, 
                                 transform=ax_geom.transAxes, 
                                 ha='center', va='top', fontsize=9,
                                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='dimgrey'))

                # --- WEATHER (Bottom Row, spans 1st column ONLY) ---
                ax_weather = fig.add_subplot(gs[-1, 0])
                
                if not self.weather_df['rain'].empty:
                    ax_weather.bar(self.weather_df['date'], self.weather_df['rain'], color='tab:blue', alpha=0.4, label='Rain')
                    ax_weather.set_ylabel('Rain (mm)', fontsize=8, color='tab:blue')
                    
                if not self.weather_df['temp'].empty:
                    ax_temp = ax_weather.twinx()
                    ax_temp.plot(self.weather_df['date'], self.weather_df['temp'], color='tab:red', alpha=0.7)
                    ax_temp.set_ylabel('Temp (°C)', fontsize=8, color='tab:red')
                
                ax_weather.grid(True, ls='--', alpha=0.3)
                ax_weather.tick_params(labelsize=8)
                
                # Apply the same x-limits to the weather plot to guarantee alignment with resistivity plots
                ax_weather.set_xlim(self.start, self.end)
                format_time_axis(ax_weather)