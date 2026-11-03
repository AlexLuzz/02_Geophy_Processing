import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

def format_febus_das_febus_data(febus_meta, febus_data):
    times = febus_data['fa1-26110351/Source1/time']

    d_strain = np.array(febus_data['fa1-26110351/Source1/Zone1/Strain Rate [nStrain|s]'])
    #o = [-27, 0, 0]
    o = febus_meta['Origin']
    #spacing = [4.8 * 1992/1985, 0, 0][0]
    spacing = febus_meta['Spacing'][0]
    e = febus_meta['Extent']

    first_distance_point = o[0] + spacing*e[0]
    last_distance_point = o[0] + spacing*e[1]
    gauges = np.arange(first_distance_point, last_distance_point + spacing, spacing)

    return gauges, times, d_strain, spacing
