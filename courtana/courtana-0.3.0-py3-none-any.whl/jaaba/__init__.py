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
    Flytracker.

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
