from config.paths import ProjectPaths
from src.loaders.das_loader import DASLoader

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from zoneinfo import ZoneInfo
import matplotlib.dates as mdates
import pandas as pd

if __name__ == "__main__":
    paths = ProjectPaths(user='AQ96560', project_name='DAS_MCM_Tap_test') 
    
    loader = DASLoader(site_id="MCM_DAS_01")

    das_files = [
        "SR_DS_2026-10-28_18-32-41_UTC.h5",
        "SR_DS_2026-10-28_18-42-41_UTC.h5",
        "SR_DS_2026-10-28_18-52-41_UTC.h5",
        "SR_DS_2026-10-28_19-12-41_UTC.h5",
        "SR_DS_2026-10-28_19-22-41_UTC.h5",
        "SR_DS_2026-10-28_19-32-41_UTC.h5",
        "SR_DS_2026-10-28_19-42-41_UTC.h5",
        "SR_DS_2026-10-28_19-52-41_UTC.h5",
        "SR_DS_2026-10-28_20-02-41_UTC.h5"
        ]

    data = loader.load_h5(source=paths.MCM_DAS_TAP_TEST_DATA / das_files[4])
    
    m, data = loader.retrieve_febus_h5(show=True)

    t = data['fa1-26110351/Source1/time']
    tz = ZoneInfo("America/Toronto")

    t_datetime = [datetime.fromtimestamp(float(ts), tz=tz) for ts in t]

    t_start, t_end = t_datetime[0], t_datetime[-1]

    csv_arpentage = pd.read_csv(
        paths.MCM_DAS_TAP_TEST_ARPENTAGE / "MCM_2026A2_TapTest_XYZ.csv",
        sep=";")

    x_arp = csv_arpentage['chainage']# + 3
    x_arp = x_arp + (x_arp > 600) #* - 7

    t_arp = pd.to_datetime(csv_arpentage['Averaging start'], errors='coerce', utc=True).dt.tz_convert(tz)

    mask = t_arp.between(t_start, t_end)

    x_arp_window = x_arp[mask].to_numpy()
    t_arp_window = t_arp[mask]

    d = np.array(data['fa1-26110351/Source1/Zone1/Strain Rate [nStrain|s]'])
    o = m['Origin']
    s = [4.8 * 1992/1985, 0, 0] # m['Spacing']
    e = m['Extent']

    first_distance_point = o[0] + s[0]*e[0]
    last_distance_point = o[0] + s[0]*e[1]
    x = np.arange(first_distance_point, last_distance_point + s[0], s[0])

    # Spatial mask: retain gauges within the arpentage distance range
    mask_x = (x >= x_arp_window.min()) & (x <= x_arp_window.max())

    # Apply mask to third dimension
    d = d[:, :, mask_x]
    x = x[mask_x]

    n_sub = 5  # Average every 10 samples (880 -> 88 samples/second)

    n_time, n_samples, n_gauges = d.shape

    # Average groups of n_sub along the high-frequency time axis
    n_groups = n_samples // n_sub

    d_strain = d[:, :n_groups * n_sub, :].reshape(n_time, n_groups, n_sub, n_gauges).mean(axis=2)

    # Flatten seconds and subsamples into one continuous time axis
    d_strain = d_strain.reshape(-1, n_gauges)

    fig, ax = plt.subplots(figsize=(12, 6))

    from matplotlib.colors import SymLogNorm, Normalize

    #norm = SymLogNorm(linthresh=500, linscale=1, vmin=-10000, vmax=10000, base=10)
    norm = Normalize(vmin=-2500, vmax=2500)

    image = ax.imshow(
        d_strain,  # No transpose here
        aspect="auto",
        origin="lower",
        interpolation="nearest",
        extent=[
            x[0] - s[0]/2,
            x[-1] + s[0]/2,
            mdates.date2num(t_start),
            mdates.date2num(t_end)
        ],
        cmap="Spectral_r",
        norm=norm
    )

    ax.yaxis_date()
    ax.autoscale(enable=False)
    ax.yaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S", tz=tz))
    ax.set(xlabel="Fiber position (m)", ylabel="Time")

    ax.scatter(
        x_arp_window,
        mdates.date2num(t_arp_window.dt.to_pydatetime()),
        s=5,
        color="black"
    )

    from matplotlib.ticker import MaxNLocator

    # X-axis: maximum number of ticks
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10))

    fig.colorbar(image, ax=ax, label="Magnitude (nStrain/s)")
    fig.tight_layout()
    plt.show()
