import numpy as np

from ..tools import wrap_angles


def _rolling_window(a, window):
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def _cover_neighbors(a, n=1, true_min=None, true_max=None):
    """Include in the array the n neighboring values.
    If no true limits are given, it respects the array minimum and
    maximum values.
    Ex:
    a = [0, 5, 8]; n = 1
    Return: [0, 1, 4, 5, 6, 7, 8, 9]
    """
    true_min = true_min if true_min is not None else a.min()
    true_max = true_max if true_max is not None else a.max()
    b = []
    for value in a:
        for i in range(1, n + 1):
            new_value = value - i
            if not new_value < true_min:
                b.append(new_value)

            new_value = value + i
            if not new_value > true_max:
                b.append(new_value)
        else:
            b.append(value)
    return np.array(sorted(list(set(b))))


def fix_pi_flips(s, tolerance=0.45):
    """Fix pi radians flips in a `pandas.Series`.
    s:         Series values must be contained in the interval [-pi, pi].
    tolerance: radians
    """
    s_tmp = s.copy()
    for i, (prev, curr) in enumerate(_rolling_window(s_tmp, window=2)):
        curr_index = i + 1
        diff = curr - prev
        if np.pi - tolerance <= abs(diff) <= np.pi + tolerance:
            s_tmp[curr_index] -= np.sign(diff) * np.pi

    return wrap_angles(s_tmp)


def fix(df, flip_tolerance=0.45, min_body_area=100):
    """Fix a DataFrame.

    Fixes:
        - 180º orientation flips
        - Frames where `body area` is less than specified are set to NaN
          for future interpolation.
    """

    bad_frames = np.array([])

    # Retrieve the frames where NaNs occur
    frames_with_nans = df.isnull().any(axis=1).nonzero()[0]
    bad_frames = np.append(bad_frames, frames_with_nans)

    # Retrive the frames where the detected blob do not meet a minimum size
    problematic_blob_frames = df['body_area'] < min_body_area
    bad_frames = np.append(
        bad_frames,
        problematic_blob_frames[problematic_blob_frames].index
    )

    # Stretch to cover also their neighbors
    bad_frames = _cover_neighbors(
        bad_frames,
        n=1,
        true_min=problematic_blob_frames.index.min(),
        true_max=problematic_blob_frames.index.max(),
    )

    # Set all these problematic frames to NaN
    df.loc[bad_frames] = np.nan

    # # Where orientation is missing, use the previous known value
    # df['angle'] = df['angle'].ffill()

    # Interpolate the other columns
    df = df.interpolate(limit_direction='both').bfill()

    # Fix 180º flips
    df['angle'] = fix_pi_flips(df['angle'], tolerance=flip_tolerance)

    return df.copy()
