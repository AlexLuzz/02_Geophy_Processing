import pandas as pd
from pathlib import Path
from src.visualization.report_base import ReportBase
from src.visualization.DAS.basic_das import *
from src.loaders.das_loader import DASLoader 
from matplotlib.colors import SymLogNorm, Normalize
from zoneinfo import ZoneInfo

class TaptestReport(ReportBase):
    def __init__(
                self, 
                folder_path: str | Path, 
                survey_csv: object, 
                file_list: list[str],
                filename: str = "DAS_TapTest_report.pdf",
                pages: list[str] = ["waterfall", "rms"],):
        
        folder_path = Path(folder_path)
        super().__init__(folder_path / filename)

        self.survey_csv = survey_csv
        self.file_list = file_list

        self.pages = pages

        self.x_arp = self.survey_csv['chainage']
        self.t_arp = self.survey_csv['Averaging start']
        self.tz = ZoneInfo("America/Toronto")
        self.t_arp = pd.to_datetime(self.t_arp, errors='coerce', utc=True).dt.tz_convert(self.tz)


    @classmethod
    def print(cls, *args, **kwargs):
        with cls(*args, **kwargs) as report:
            report.build()

    def build(self):
        if "waterfall" in self.pages:
            self._print_waterfalls()

        if "rms" in self.pages:
            self._print_rms_pages()

    def _print_waterfalls(self):

        for file in self.file_list:
            with self.page(rows=1, cols=1, landscape=True) as (fig, gs):

                ax = fig.add_subplot(gs[:,:])

                loader = DASLoader(site_id="MCM_DAS_TapTest")
                data = loader.load_h5(source=file)
                meta, data = loader.retrieve_febus_h5(show=False)

                gauges, times, d_strain, spacing = format_febus_das_febus_data(meta, data)

                times = [datetime.fromtimestamp(float(ts), tz=self.tz) for ts in times]

                t_start, t_end = times[0], times[-1]
                mask = self.t_arp.between(t_start, t_end)
                
                x_arp_window = self.x_arp[mask].to_numpy()
                t_arp_window = self.t_arp[mask]

                mask_gauges = (gauges >= x_arp_window.min()) & (gauges <= x_arp_window.max())
                d_strain = d_strain[:, :, mask_gauges]
                gauges = gauges[mask_gauges]
                
                norm = Normalize(vmin=-2500, vmax=2500)
            
                image = plot_das_waterfall(
                    ax, gauges, times, d_strain, spacing, 
                    sub_factor=5, norm=norm)

                ax.autoscale(enable=False)
                ax.yaxis_date()
                ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S", tz=self.tz))
            
                ax.scatter(
                    x_arp_window,
                    mdates.date2num(t_arp_window.dt.to_pydatetime()),
                    s=5, color="black")
            
                fig.colorbar(image, ax=ax, label="Magnitude (nStrain/s)")

    def _print_rms_pages(self):
        pass
        