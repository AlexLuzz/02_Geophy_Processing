import pandas as pd
from pathlib import Path
from src.visualization.report_base import ReportBase
from src.visualization.basic_plotting import format_time_axis
from src.visualization.HYDRO.basic_hydrogeo import *

class HydroDataReport(ReportBase):
    def __init__(self, folder_path: str | Path, 
                 sensor_loader: object, 
                 sensor_metadata: dict,
                 filename: str = "_raw_data_report.pdf",
                 weather_df: pd.DataFrame = None):
        
        folder_path = Path(folder_path)
        super().__init__(folder_path / filename)

        self.dict_stations_df = sensor_loader.file_dict
        self.sensor_metadata = sensor_metadata 
        self.weather_df = weather_df if weather_df is not None else None
        
    @classmethod
    def print(cls, *args, **kwargs):
        with cls(*args, **kwargs) as report:
            report.build()

    def build(self):
        self._print_cover_page()
        self._build_pages()

    def _print_cover_page(self):
        with self.page() as (fig, gs):
            ax = fig.add_subplot(gs[0, 0])
            ax.axis('off')
            
            # Formatted log text displaying basic dataset characteristics
            log_text = (
                f"RAW DATASET LOG\n"
                f"{'='*30}\n"
                f"Total stations: {len(self.dict_stations_df)}\n"
                f"Station names: {', '.join(self.dict_stations_df.keys())}\n\n"
            )
            ax.text(0.05, 0.95, log_text, transform=ax.transAxes, fontsize=8, 
                    family='monospace', va='top')

    def _build_pages(self):

        for i, (s_name, s_df) in enumerate(self.dict_stations_df.items()):
            print(f"Building page for station: {s_name} ({i+1}/{len(self.dict_stations_df)})")
            start, end = s_df['TIMESTAMP'].min(), s_df['TIMESTAMP'].max()
            with self.page(rows=2, cols=2, width_ratios=[3, 0.5], landscape=True) as (fig, gs):
                ax_ts = fig.add_subplot(gs[0, 0])
                for col in s_df.filter(like='VWC').columns:
                    ax_ts.plot(s_df['TIMESTAMP'], s_df[col], label=col)
                ax_ts.set_xlim(start, end)
                format_time_axis(ax_ts, format="%Y-%m-%d")

                ax_strati = fig.add_subplot(gs[0, 1])
                plot_profile(ax_strati, self.sensor_metadata, s_name)

                ax_wf = fig.add_subplot(gs[1, 0])
                norm, cmap, _ = build_vwc_norm_cmap()
                plot_waterfall_v1(ax_wf, s_df, cmap, norm)