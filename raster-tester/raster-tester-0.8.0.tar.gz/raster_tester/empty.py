import click, sys

import numpy as np
import rasterio as rio

def array_hasdata(arr):
    return np.any(arr)

def is_empty(input_path, randomize, bidx):
    with rio.open(input_path) as src:
        windows = [window for ij, window in src.block_windows()]

        if randomize:
            np.random.shuffle(windows)

        empty = True

        for window in windows:
            if array_hasdata(src.read(bidx, window=window)):
                empty = False
                break

        return empty
