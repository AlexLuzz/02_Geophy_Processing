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

    data = loader.load_h5(source=paths.MCM_DAS_TAP_TEST_DATA / das_files[0])
    
    m, data = loader.retrieve_febus_h5(show=True)

    t = data['fa1-26110351/Source1/time']
    tz = ZoneInfo("America/Toronto")

    t_datetime = [datetime.fromtimestamp(float(ts), tz=tz) for ts in t]

    t_start, t_end = t_datetime[0], t_datetime[-1]

    csv_arpentage = pd.read_csv(
        paths.MCM_DAS_TAP_TEST_ARPENTAGE / "MCM_2026A2_TapTest_XYZ.csv",
        sep=";")

    x_arp = csv_arpentage['chainage']
    #x_arp = x_arp + (x_arp > 600) * - 7

    t_arp = pd.to_datetime(
        csv_arpentage['Averaging start'],
        errors='coerce',
        utc=True
    ).dt.tz_convert(tz)

    d = np.array(data['fa1-26110351/Source1/Zone1/Strain Rate [nStrain|s]'])
    o = [-25, 0, 0]# m['Origin']
    s = [4.8 * 1985/1992, 0, 0] # m['Spacing']
    e = m['Extent']

    first_distance_point = o[0] + s[0]*e[0]
    last_distance_point = o[0] + s[0]*e[1]
    x = np.arange(first_distance_point, last_distance_point + s[0], s[0])

    point_idx = t_arp[t_arp > t_start].index[9]

    x_selected = csv_arpentage.loc[point_idx, "chainage"]
    t_selected = t_arp.loc[point_idx]
    
    # DAS parameters
    fs = 880
    before, after = -0.5, 6
    n_sub = int(fs * 0.250)  # 220 samples

    # Flatten time dimension: (600*880, 416)
    d_flat = d.reshape(-1, d.shape[-1])

    # Locate surveyed timestamp
    sample_idx = round(
        (t_selected.timestamp() - t_datetime[0].timestamp()) * fs)

    # Extract 5-second window
    i0 = sample_idx - int(before * fs)
    i1 = sample_idx + int(after * fs)

    d_window = d_flat[i0:i1]

    # Calculate RMS every 250 ms
    n_groups = len(d_window) // n_sub

    d_sub = d_window[:n_groups*n_sub].reshape(
        n_groups, n_sub, d.shape[-1]
    )

    rms = np.sqrt(np.mean(d_sub**2, axis=1))

    # Plot
    fig, ax = plt.subplots(figsize=(12, 5))

    colors = plt.cm.turbo(np.linspace(0, 1, n_groups))

    for i, (r, color) in enumerate(zip(rms, colors)):
        ax.plot(x, r, color=color, label=f"{-before + i*0.25:.2f} s")

    ax.axvline(x_selected, color="black", ls="--", label="Surveyed point")

    ax.set(
        xlabel="Fiber position (m)",
        ylabel="RMS strain rate (nStrain/s)"
    )

    sm = plt.cm.ScalarMappable(
        cmap="turbo",
        norm=plt.Normalize(-before, after)
    )
    fig.colorbar(sm, ax=ax, label="Time relative to surveyed point (s)")

    ax.set_xlim(x_selected - 50, x_selected + 50)
    ax.set_ylim(0, 10000)

    ax.legend(fontsize=7)
    fig.tight_layout()
    plt.show()