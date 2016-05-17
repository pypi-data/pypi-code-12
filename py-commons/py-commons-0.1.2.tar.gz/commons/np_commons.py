import numpy as np


def weighted_percentile(arr, weights, percentiles):
    """
    Evaluate weighted percentiles.
    :param arr: vector
    :param weights: weight array
    :param percentiles: percentiles array with values between 0 and 100
    :return: array of the same dim as percentiles.
    """
    arr = np.array(arr, copy=True, dtype=float)
    weights = np.array(weights, copy=True, dtype=float)
    percentiles = np.array(percentiles, copy=True, dtype=float) / 100.0

    assert hasattr(arr, 'shape') and len(arr.shape) == 1, 'Can only evaluate percentile for 1-dim arrays'
    assert hasattr(percentiles, 'shape') and len(percentiles.shape) == 1, 'Percentiles must be 1-dim array'
    assert hasattr(weights, 'shape') and weights.shape == arr.shape, 'Array and weights shapes must be equal'
    assert np.all(percentiles <= 1.0) and np.all(percentiles >= 0.0), 'Percentiles must be in range [0, 100]'

    sort_idx = np.argsort(arr)
    sorted_arr = arr[sort_idx]
    sorted_weight = weights[sort_idx]
    raw_percentiles = np.cumsum(sorted_weight) / sorted_weight.sum()
    return sorted_arr[np.searchsorted(raw_percentiles, percentiles, side='left')]

