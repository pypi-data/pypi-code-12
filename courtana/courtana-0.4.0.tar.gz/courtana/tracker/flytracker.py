import os

import numpy as np
import pandas as pd
from scipy.io import loadmat, savemat

from . import doctor


def fix_trackfile(path, end=None, min_body_area=100):
    """Looks for the `-track.mat` inside the output folder, applies some
    fixes and save the result in a `_fixed-track.mat` file.

    path: output folder path
    end:  the last frame to consider

    Fixes:
        - 180º orientation flips
        - Frames where `body area` is less than specified are set to NaN
          for future interpolation.
    """

    # FIXME this method is deprecated

    panel = load_trackfile(path, end=end)
    # Rename the axes
    panel.rename(
        minor_axis={
            'pos x': 'pos_x',
            'pos y': 'pos_y',
            'ori': 'angle',
            'body area': 'body_area',
        },
        inplace=True,
    )
    panel.major_axis.name = 'frame'
    dfs = [doctor.fix(panel[item]) for item in panel]

    basename = os.path.split(path)[-1]
    filepath = os.path.join(path, basename + '_fixed-track.mat')
    _save_mat(filepath, variable='trk', dfs=dfs)

    print("Saved fixed trackfile to %s" % filepath)

    # FIXME some temporary shenanigans
    return pd.Panel({item: df for item, df in zip(panel, dfs)})


def load_trackfile(path, end=None):
    """Load -track.mat contents and returns them in a pandas.Panel.

    path: output folder path
    end:  the last frame to consider

    Returns:
        pandas.Panel where axis 0 correponds to a fly (fly0 ... flyN),
        axis 1 indexes the video frames and axis 2 the data columns.
    """
    basename = os.path.split(path)[-1]
    filepath = os.path.join(path, basename + '-track.mat')
    return _load_mat(filepath, variable='trk', end=end)


def load_featfile(path, end=None):
    """Load -feat.mat contents and returns them in a pandas.Panel.

    path: output folder path
    end:  the last frame to consider

    Returns:
        pandas.Panel where axis 0 correponds to a fly (fly0 ... flyN),
        axis 1 indexes the video frames and axis 2 the data columns.
    """
    basename = os.path.split(path)[-1]
    filepath = os.path.join(path, basename + '-feat.mat')
    return _load_mat(filepath, variable='feat', end=end)


def save_trackfile(path, dfs):
    """Save DataFrames to a `*_fixed-track.mat` file.

    path: output folder path
    dfs:  list of dataframes (make sure the order of the DataFrames
          match the original, for consistency)
    """
    basename = os.path.split(path)[-1]
    filepath = os.path.join(path, basename + '-track.mat')
    _save_mat(filepath, variable='trk', dfs=dfs)


def _load_mat(path, variable, end=None):
    """Load FlyTracker output mat file.

    path:     path to a .mat file (passed to `scipy.io.loadmat`)
    variable: variable to read from within the file ('trk' ot 'feat')
    end:      the last frame to consider

    Returns:
        pandas.Panel where axis 0 correponds to a fly (fly0 ... flyN),
        axis 1 indexes the video frames and axis 2 the data columns.
    """

    mat = loadmat(path)
    mdata = mat[variable]
    mdtype = mdata.dtype
    data = {n: mdata[n][0, 0] for n in mdtype.names}

    names = pd.Series([name[0]
                       for arr in data['names']
                       for name in arr])

    panel_data = {}
    for i in range(data['data'].shape[0]):  # number of flies
        if end is None:
            df = pd.DataFrame(data['data'][i, :, :], columns=names)
        else:
            df = pd.DataFrame(data['data'][i, :end, :], columns=names)
        panel_data['fly{}'.format(i)] = df

    return pd.Panel(panel_data)


def _save_mat(path, variable, dfs):
    """Save DataFrames to a .mat file.

    path:     path to a .mat file (passed to `scipy.io.savemat`)
    variable: variable to write to the file ('trk' ot 'feat')
    dfs:      list of dataframes (make sure the order of the DataFrames
              match the original, for consistency)
    """

    mdtype_names = ['names', 'data', 'flags']

    data = dict.fromkeys(mdtype_names, np.ndarray(shape=(1, 1)))

    col_names = dfs[0].columns.values
    data['names'] = col_names.reshape((1, len(col_names)))
    data['data'] = np.array([df.values for df in dfs])
    data['flags'] = np.zeros(shape=[1, 6])

    mdata = np.ndarray(
        shape=(1, 1), dtype=[('names', 'O'), ('data', 'O'), ('flags', 'O')])

    for name in mdtype_names:
        mdata[name][0, 0] = data[name]

    savemat(path, {variable: mdata})


if __name__ == '__main__':
    panel = load_featfile('/mnt/VasconcelosDS1/teresa_msc/share/video_001')
    print(panel)
