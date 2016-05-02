import rasterio as rio
from rasterio import warp
import numpy as np


def winding_order(boundsArr):
    '''
    returns False if CCW; True is CW
    (ie, it crosses the dateline and is inverted when unprojected)
    '''
    shiftBounds = np.roll(boundsArr, -1, 0)
    delta = (shiftBounds[:, 0] - boundsArr[:, 0]) * (shiftBounds[:, 1] + boundsArr[:, 1])

    return np.sum(delta) > 0


def densify(boundsArr, dens=4):
    '''
    Adds points between the bounds corners
    '''
    denseBounds = np.zeros(
        ((boundsArr.shape[0]) * dens, 2),
        dtype=boundsArr.dtype)

    denseBounds[::dens] += boundsArr
    diffs = (boundsArr - np.roll(boundsArr, -1, 0)) / float(dens)
    for i in range(1, dens):
        denseBounds[i::dens] += boundsArr - (diffs * i)

    return denseBounds


def make_bounds_array(bounds):
    '''
    Array of raster bounds
    in counter-clockwise
    fashion
    '''
    return np.array([
        [bounds.left, bounds.bottom],
        [bounds.right, bounds.bottom],
        [bounds.right, bounds.top],
        [bounds.left, bounds.top]
        ])


def transform_bounds(boundsArr, crs):
    if not crs:
        raise ValueError('Input raster must have a CRS')

    return np.dstack(warp.transform(
            crs,
            {'init': 'epsg:4326'},
            boundsArr[:, 0],
            boundsArr[:, 1]))[0]


def crosses_dateline(fpath):
    '''
    Checks if a raster crosses the dateline after unprojection to epsg 4326
    '''
    with rio.open(fpath) as src:
        denseBounds = densify(make_bounds_array(src.bounds))
        unprojectedBounds = transform_bounds(denseBounds, src.crs)

        return winding_order(unprojectedBounds)
