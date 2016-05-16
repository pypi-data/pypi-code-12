# -*- coding: utf-8 -*-

"""
TrackData
=========

In this module I define a common data structure to be used by COURTANA.


"""

import numpy as np
import pandas as pd

from .opencsp import OpenCSPOutput


class TrackData(object):

    """
    DOCSTRING

    :param int fps: video FPS (frames per second)
    :param float pxmm: number of pixels corresponding to 1 mm
    """

    GENDERS = ("f", "m")

    DEFAULT_COLUMN_NAMES = ["pos_x", "pos_y",
                            # "angle",
                            "head_x", "head_y",
                            "tail_x", "tail_y",
                            "is_merged"]

    def __init__(self, female_df=None, male_df=None, **kwargs):
        self.f = female_df
        self.m = male_df

        if not self._check_consistency():
            raise Exception("Female and male data is not consistent")

        self.fps = kwargs.pop('fps', None)
        self.pxmm = kwargs.pop('pxmm', None)

    @classmethod
    def _prepare_test_sample(cls):
        contens = {name: np.random.random_integers(0, 10, 10)
                   for name in cls.DEFAULT_COLUMN_NAMES}
        contens['angle'] = contens['angle'].astype(float)
        return cls(pd.DataFrame(contens), pd.DataFrame(contens))

    @classmethod
    def from_OpenCSP(cls, csvfile):
        tracker_output = OpenCSPOutput(csvfile)
        tracker_output.remove_unnecessary_columns()
        tracker_output.fix_column_names()
        tracker_output.split_by_gender('blob_index')
        tracker_output.female.columns = cls.DEFAULT_COLUMN_NAMES
        tracker_output.male.columns = cls.DEFAULT_COLUMN_NAMES
        return cls(tracker_output.female, tracker_output.male)

    @classmethod
    def from_HDF(cls, filename, key='/'):
        if key[-1] != '/':
            key += '/'
        with pd.HDFStore(filename, mode='r+') as store:
            return cls(store.get(key+'f'), store.get(key+'m'))

    def _check_consistency(self):
        """Returns False in case any test fails."""
        is_consistent = True
        frames = {}
        ok_frames = {}
        missing_frames = {}
        for gender in TrackData.GENDERS:
            df = getattr(self, gender)
            frames[gender] = df.index.values
            ok_frames[gender] = df.iloc[
                df.notnull().any(axis=1).nonzero()[0]].index.values
            missing_frames[gender] = df.iloc[
                df.isnull().any(axis=1).nonzero()[0]].index.values

        # Check integrity between female and male
        if not np.array_equal(frames['f'], frames['m']):
            print("Total number of frames is different")
            is_consistent = False
        if not np.array_equal(ok_frames['f'], ok_frames['m']):
            print("Number of frames OK is different")
            is_consistent = False
        if not np.array_equal(missing_frames['f'], missing_frames['m']):
            print("Number of NaN frames is different")
            is_consistent = False
        # Print final report
        if is_consistent:
            # Only need to use one
            self.frames = frames['f']
            self.ok_frames = ok_frames['f']
            self.missing_frames = missing_frames['f']
        return is_consistent

    def consistency_report(self):
        """Prints out overall info about the data."""
        report = (
            "Frames (Total/Ok/NaN/Missing%): {:^6} / {:^6} / {:^6} / {:^3.0f}"
        )
        return report.format(
            len(self.frames),
            len(self.ok_frames),
            len(self.missing_frames),
            100 * len(self.missing_frames) / len(self.frames)
        )

    def save(self, filename, key='/'):
        """Saves to an HDF5 store."""
        if key[-1] != '/':
            key += '/'
        with pd.HDFStore(filename, mode='w') as store:
            for g in self.GENDERS:
                df = getattr(self, g)
                store.put(key+g, df,
                          append=False,  # overwrite
                          format='table',
                          data_columns=True,
                          encoding='utf-8',
                          dropna=False)

    def load(self, filename, key='/'):
        """Loads two DataFrames from an HDF5 file."""
        with pd.HDFStore(filename) as store:
            for g in self.GENDERS:
                setattr(self, g, store.get(key+g))
