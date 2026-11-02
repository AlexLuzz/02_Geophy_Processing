import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

def format_febus_das_febus_data(febus_meta, febus_data):
    times = febus_data['fa1-26110351/Source1/time']

    d_strain = np.array(febus_data['fa1-26110351/Source1/Zone1/Strain Rate [nStrain|s]'])
    o = febus_meta['Origin']
    spacing = [4.8 * 1992/1985, 0, 0][0] # febus_meta['Spacing']
    e = febus_meta['Extent']

    first_distance_point = o[0] + spacing*e[0]
    last_distance_point = o[0] + spacing*e[1]
    gauges = np.arange(first_distance_point, last_distance_point + spacing, spacing)

    return gauges, times, d_strain, spacing

def plot_das_waterfall(ax, gauges, times, d_strain, spacing, sub_factor=5, norm=None):

    n_time, n_samples, n_gauges = d_strain.shape
                
    # Average every n_sub samples along the acquisition time axis
    d_strain = d_strain.reshape(n_time, 
                                n_samples // sub_factor, 
                                sub_factor, 
                                n_gauges).mean(axis=2)

    # Flatten seconds and subsamples into a continuous time axis
    d_strain = d_strain.reshape(-1, n_gauges)
    
    image = ax.imshow(
        d_strain,
        aspect='auto',
        origin="lower",
        interpolation="nearest",
        extent=[gauges.min(), gauges.max(), times[-1], times[0]],
        cmap="Spectral_r",
        norm=norm
    )

    ax.set(xlabel="Fiber position (m)", ylabel="Time")

    return image