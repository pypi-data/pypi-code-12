"""
Tools to work with the classification output from JAABA.
"""

import logging
import os

from scipy.io import loadmat
import pandas as pd


log = logging.getLogger(__name__)


def read_behavior_predictions(output_folder, target, behavior):
    """Read JAABA behavior predictions of a movie processed using
    FlyTracker.

    output_folder: path to FlyTracker output folder of a video
    target:        number of the fly as JAABA labeled it (0,...,N)
    behavior:      behavior name of the jab file

    Returns a boolean pandas.Series whose indexes are the frames and the
    truthfulness indicating the behavior prediction.
    """
    foldername = os.path.split(output_folder)[-1]
    scores_filepath = os.path.join(
        output_folder, foldername + '_JAABA', 'scores_' + behavior + '.mat')

    log.info(scores_filepath)

    mat = loadmat(scores_filepath)
    mdata = mat['allScores']
    scores = {n: mdata[n][0, 0] for n in mdata.dtype.names}

    return pd.Series(scores['postprocessed'][0, target][0], dtype=bool)


def read_flytracker_mat(output_folder, variable='feat', endframe=None):
    # TODO Docs!
    # FIXME DEPRECATED
    # should use the methods available in the flytracker module
    filename = os.path.split(output_folder)[-1]
    data_filepath = os.path.join(output_folder, filename + '-' + variable)

    if variable == 'track':
        variable = 'trk'

    mat = loadmat(data_filepath)
    mdata = mat[variable]
    mdtype = mdata.dtype
    ndata = {n: mdata[n][0, 0] for n in mdtype.names}

    names = pd.Series([name[0] for arr in ndata['names'] for name in arr])
    if variable == 'trk':
        units = None
    else:
        units = pd.Series([unit for arr in ndata['units'] for unit in arr])

    if endframe is None:
        df1 = pd.DataFrame(ndata['data'][0, :, :], columns=names)
        df2 = pd.DataFrame(ndata['data'][1, :, :], columns=names)
    else:
        df1 = pd.DataFrame(ndata['data'][0, :endframe, :], columns=names)
        df2 = pd.DataFrame(ndata['data'][1, :endframe, :], columns=names)

    return df1, df2, units
