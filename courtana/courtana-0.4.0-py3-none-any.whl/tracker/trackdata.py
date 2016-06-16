# -*- coding: utf-8 -*-

"""
TrackData
=========

In this module I define a common data structure to be used by COURTANA.


"""

import numpy as np
import pandas as pd
from scipy.spatial import distance
import matplotlib.pyplot as plt

from . import doctor
from . import flytracker
from .opencsp import OpenCSPOutput
from ..courtana import GENDER_COLOR
from ..tools import wrap_angles


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
    def from_FlyTracker(cls, output_folder, f, m, *args, **kwargs):
        """Create a TrackData object from Eyrun's FlyTracker output
        folder.
        Both the -track.mat and -feat.mat files are required. FIXME
        Pass the panel item name to `f` or `m` do indicate which are the
        female and the male respectively.

        Note 1: TrackData only support two flies, a female and a male.
        Note 2: All wing and leg data are ignored. For now.
        Note 3: `track` is interpolated; `feat` is not touched.
        """

        fix_kwargs = {
            'min_body_area': kwargs.pop('min_body_area', 100),
            'flip_tolerance': kwargs.pop('flip_tolerance', 0.45),
        }

        # Load original track data
        track_panel = flytracker.load_trackfile(output_folder, *args, **kwargs)

        # Exclude not used data columns
        valid_columns = ['pos x', 'pos y', 'ori', 'body area']
        track_panel = track_panel.select(
            lambda x: any(s in x for s in valid_columns), axis=2)

        # Rename the axes
        track_panel.rename(
            minor_axis={
                'pos x': 'pos_x',
                'pos y': 'pos_y',
                'ori': 'angle',
                'body area': 'body_area',
            },
            inplace=True,
        )
        track_panel.major_axis.name = 'frame'

        # Fix the data and assign the male and female DataFrames
        f_df = doctor.fix(track_panel[f], **fix_kwargs)
        m_df = doctor.fix(track_panel[m], **fix_kwargs)

        return cls(f_df, m_df)

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

    def plot(self, frame):
        f_x = self.f.pos_x[frame]
        f_y = self.f.pos_y[frame]
        f_a = self.f.angle[frame]

        m_x = self.m.pos_x[frame]
        m_y = self.m.pos_y[frame]
        m_a = self.m.angle[frame]

        # minus sign required because video y-axis is inverted
        # here I invert the y position also, but could have also applied
        # to the sin()
        xyuv = [
            [f_x, -f_y, np.cos(f_a), np.sin(f_a), GENDER_COLOR['f']],
            [m_x, -m_y, np.cos(m_a), np.sin(m_a), GENDER_COLOR['m']]
        ]
        x, y, u, v, c = zip(*xyuv)
        plt.quiver(x, y, u, v, color=c, units='xy', angles='xy')

        plt.text(800, -950,
                 'af = %.1f\N{DEGREE SIGN}' % (np.degrees(f_a)),
                 color='k', size=14)
        plt.text(800, -850,
                 'am = %.1f\N{DEGREE SIGN}' % (np.degrees(m_a)),
                 color='k', size=14)

        plt.text(800, -750,
                 'a m-f = %.1f\N{DEGREE SIGN}' % (np.degrees(m_a-f_a)),
                 color='k', size=14)
        plt.text(800, -650,
                 'a f-m = %.1f\N{DEGREE SIGN}' % (np.degrees(f_a-m_a)),
                 color='k', size=14)

        video_size = 1024  # FIXME
        plt.xlim(0, video_size)
        plt.ylim(-video_size, 0)

    # =========================================================================
    # Methods to add columns to the TrackData

    def convert_frames_to_seconds(self, fps):
        """Assumes DataFrames index are the frames and creates and
        column with the corresponding seconds.
        """
        for gender in self.GENDERS:
            df = getattr(self, gender)
            df['time'] = df.index / fps

    def convert_to_mm(self, colname, pxmm):
        for gender in self.GENDERS:
            df = getattr(self, gender)
            df[colname+'_mm'] = df[colname] / pxmm

    def add_speed(self):
        """Add the fly's speed."""
        for gender in self.GENDERS:
            df = getattr(self, gender)
            pos = df[['time', 'pos_x_mm', 'pos_y_mm']]
            disp = pos.diff()  # displacement
            df['speed'] = (np.sqrt(disp['pos_x_mm']**2 + disp['pos_y_mm']**2) /
                           disp['time']).bfill()

    def add_dist_to_other(self):
        """Add the distance from one fly to the other."""
        # The distance between them is calculated only once and added to both
        # Works because we only have two flies

        f_pos = self.f[['pos_x_mm', 'pos_y_mm']]
        m_pos = self.m[['pos_x_mm', 'pos_y_mm']]

        # Merge the x and y coordinates in the form (x, y) to use euclidean
        f_pos_xy = f_pos.apply(
            lambda x: [x['pos_x_mm'], x['pos_y_mm']], axis=1).values
        m_pos_xy = m_pos.apply(
            lambda x: [x['pos_x_mm'], x['pos_y_mm']], axis=1).values

        dist = np.array([distance.euclidean(p1, p2)
                         for p1, p2 in zip(f_pos_xy, m_pos_xy)])

        self.f['dist_to_other'] = dist
        self.m['dist_to_other'] = dist

    def add_angle_to_other(self):
        """Add the angle a flies does towards the other."""
        self.f['angle_to_other'] = wrap_angles(
            self.f['angle'] - self.m['angle']
        )
        self.m['angle_to_other'] = wrap_angles(
            self.m['angle'] - self.f['angle']
        )
