import pandas as pd
from pathlib import Path
from src.visualization.report_base import ReportBase
from src.visualization.DAS.basic_das import *
from src.loaders.das_loader import DASLoader 
from matplotlib.colors import SymLogNorm, Normalize
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt

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
            self._print_pages()

    def _print_pages(self):
        for file in self.file_list:

            loader = DASLoader(site_id="MCM_DAS_TapTest")
            data = loader.load_h5(source=file)
            meta, data = loader.retrieve_febus_h5(show=False)

            gauges, times, d_strain, spacing = format_febus_das_febus_data(meta, data)

            times = pd.DatetimeIndex(
                [datetime.fromtimestamp(float(ts), tz=self.tz) for ts in times]
            )
            # Only keep surveyed points in the das file timeframe
            t_start, t_end = times[0], times[-1]
            mask = self.t_arp.between(t_start, t_end)
            x_arp_window = self.x_arp[mask].to_numpy()
            t_arp_window = self.t_arp[mask]

            # Only keep gauges within the arpentage distance range, with a margin
            margin = 15  # meters

            mask_gauges = (
                (gauges >= x_arp_window.min() - margin) &
                (gauges <= x_arp_window.max() + margin))
            
            d_strain = d_strain[:, :, mask_gauges] # gauges is the third dimension of data
            gauges = gauges[mask_gauges]

            if "waterfall" in self.pages:
                with self.page(rows=1, cols=1, landscape=True) as (fig_wtf, gs_wtf):

                    ax_wtf = fig_wtf.add_subplot(gs_wtf[:, :])

                    norm = Normalize(vmin=-2500, vmax=2500)

                    n_time, n_samples, n_gauges = d_strain.shape
                    n_sub = 5

                    # Average every n_sub samples along the acquisition time axis
                    d_waterfall = d_strain.reshape(
                        n_time, n_samples // n_sub, n_sub, n_gauges
                    ).mean(axis=2).reshape(-1, n_gauges)

                    image = ax_wtf.imshow(
                        d_waterfall,
                        aspect="auto",
                        origin="lower",
                        interpolation="nearest",
                        extent=[
                            gauges.min() - spacing/2,
                            gauges.max() + spacing/2,
                            times[0], times[-1]
                        ],
                        cmap="Spectral_r",
                        norm=norm
                    )

                    ax_wtf.set(xlabel="Fiber position (m)", ylabel="Time")
                    ax_wtf.autoscale(enable=False)
                    ax_wtf.yaxis_date()
                    ax_wtf.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S", tz=self.tz))

                    ax_wtf.scatter(x_arp_window, t_arp_window, s=5, color="black")

                    for i in range(len(x_arp_window)):
                        if i == 0 or (i + 1) % 5 == 0:
                            ax_wtf.annotate(
                                str(i + 1),
                                (x_arp_window[i] + 2.5, t_arp_window.iloc[i] - pd.Timedelta(seconds=5)),
                                xytext=(4, 0),
                                textcoords="offset points",
                                fontsize=7,
                                va="center",
                                bbox=dict(boxstyle="square,pad=0.2", fc="white", ec="black", alpha=0.8))

                    fig_wtf.colorbar(image, ax=ax_wtf, label="Magnitude (nStrain/s)")

            if "rms" in self.pages:
                n_plot_per_page = 8
                n_pages = (len(x_arp_window) + n_plot_per_page - 1) // n_plot_per_page

                fs = 880
                before, after = -0.5, 6
                n_sub = int(fs * 0.500)

                d_flat = d_strain.reshape(-1, len(gauges))

                errors = []

                for page in range(n_pages):
                    with self.page(rows=10, cols=1, landscape=False, hspace=0) as (fig_rms, gs_rms):

                        axes = []

                        for j, i in enumerate(range(
                            page * n_plot_per_page,
                            min((page + 1) * n_plot_per_page, len(x_arp_window))
                            )):
                            ax_rms = fig_rms.add_subplot(gs_rms[j, 0], sharex=axes[0] if axes else None)
                            axes.append(ax_rms)

                            # Locate surveyed timestamp
                            t_arp = t_arp_window.iloc[i]
                            sample_idx = round((t_arp.timestamp() - times[0].timestamp()) * fs)

                            # Extract time window
                            i0 = sample_idx - int(before * fs)
                            i1 = sample_idx + int(after * fs)
                            d_window = d_flat[i0:i1]

                            # Calculate RMS every 250 ms
                            n_groups = len(d_window) // n_sub
                            d_sub = d_window[:n_groups * n_sub].reshape(
                                n_groups, n_sub, len(gauges)
                            )
                            rms = np.sqrt(np.mean(d_sub**2, axis=1))

                            # Find RMS peak within +/- 20 m of surveyed position
                            x0 = x_arp_window[i]
                            mask = np.abs(gauges - x0) <= 20

                            # Maximum RMS over time
                            signal = rms[:, mask].max(axis=0)
                            x = gauges[mask]

                            # Weighted centroid of the peak
                            baseline = np.min(signal)
                            weights = np.maximum(signal - baseline, 0)

                            peak_position = np.sum(x * weights) / np.sum(weights)
                            error = peak_position - x0
                            
                            errors.append(error)

                            colors = plt.cm.turbo(np.linspace(0, 1, n_groups))

                            for k, (r, color) in enumerate(zip(rms, colors)):
                                ax_rms.plot(gauges, r, color=color, 
                                        label=f"Point {i + 1} - {x_arp_window[i]:.1f} m" if k == 0 else None)

                            ax_rms.axvline(x_arp_window[i], color="black", ls="--")
                            ax_rms.set_title("")
                            ax_rms.set_ylabel("")

                            ax_rms.legend(fontsize=8, 
                                loc="upper right" if i < len(x_arp_window) / 2 else "upper left")

                            ax_rms.text(
                                0.87, 0.05,
                                f"Error: {error:+.2f} m",
                                transform=ax_rms.transAxes, fontsize=7,
                                bbox=dict(boxstyle="square,pad=0.2", fc="white", ec="black", alpha=0.8)
                            )

                        for ax in axes[:-1]:
                            ax.tick_params(axis="x", labelbottom=False)

                        axes[-1].tick_params(axis="x", labelbottom=True)
                        axes[-1].set_xlabel("Fiber position (m)")
                        fig_rms.supylabel("RMS strain rate (nStrain/s)")

                        # One shared colorbar per page
                        sm = plt.cm.ScalarMappable(
                            cmap="turbo",
                            norm=plt.Normalize(0, after - before)
                        )
                        fig_rms.colorbar(sm, ax=fig_rms.axes, 
                        label="Time relative to surveyed point (s)")

                with self.page(rows=1, cols=1, landscape=False, hspace=0) as (fig, gs):
                    errors = np.array(errors)

                    ax = fig.add_subplot(gs[:, :])
                    ax.hist(errors, bins=20, edgecolor="black")
                    ax.set_xlabel("Error (m)")
                    ax.set_ylabel("Count")
                    ax.set_title("Histogram of errors between surveyed and DAS peak positions")

                    stats = (
                        f"Mean error:   {np.mean(errors):+.2f} m\n"
                        f"Median error: {np.median(errors):+.2f} m\n"
                        f"Highest error: {np.max(np.abs(errors)):.2f} m\n"
                        f"Lowest error:  {np.min(np.abs(errors)):.2f} m"
                    )

                    ax.text(
                        0.99, 0.99, stats,
                        transform=ax.transAxes,
                        ha="left", va="top",
                        fontsize=9,
                        bbox=dict(boxstyle="round", fc="white", alpha=0.85)
                    )

