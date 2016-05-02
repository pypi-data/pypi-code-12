#!/usr/bin/env python

from affine import Affine
import click
import numpy as np
import rasterio
from rasterio.warp import reproject, RESAMPLING
from rasterio.coords import BoundingBox

from .utils import exception_raiser


def affaux(up):
    return Affine(1, 0, 0, 0, -1, 0), Affine(up, 0, 0, 0, -up, 0)


def upsample_array(bidx, up, fr, to):
    upBidx = np.empty(
        (bidx.shape[0] * up, bidx.shape[1] * up), dtype=bidx.dtype)

    reproject(
        bidx, upBidx,
        src_transform=fr,
        dst_transform=to,
        src_crs="EPSG:3857",
        dst_crs="EPSG:3857",
        resampling=RESAMPLING.bilinear)

    return upBidx

def array_compare(arr1, arr2, valueFilter=0, countFilter=0, debug=False):
    diffArr = np.abs(arr1.astype(np.int64) -
                     arr2.astype(np.int64)).astype(arr1.dtype)

    diffSpots = np.where(diffArr > valueFilter)

    diffCount = diffSpots[0].size

    if debug and diffCount > countFilter:
        rows, cols = arr1.shape
        divver = int(np.mean([rows, cols])) / 60 + 1
        mapa = ['-', 'X']
        diffPlot = (np.histogram2d(diffSpots[0], diffSpots[1], (np.arange(
            0, cols, divver * 2), np.arange(0, rows, divver)))[0] > 0).astype(np.uint8)
        click.secho('\n'.join([''.join([mapa[i] for i in row])
                               for row in diffPlot]), fg='red')

    return diffCount, diffCount > countFilter


def make_fill_array(height, width, downsample, dtype):
    return np.zeros(
        (int(height / downsample), int(width / downsample)),
        dtype
    )


def compare_properties(src1, src2, properties, tol=1e-6):
    noMatch = []
    for prop in properties:
        a = src1.__getattribute__(prop)
        b = src2.__getattribute__(prop)
        equal = True
        if isinstance(a, BoundingBox) and isinstance(b, BoundingBox):
            for coord_a, coord_b in zip(tuple(a), tuple(b)):
                if abs(coord_a - coord_b) > tol:
                    equal = False
                    break
        elif isinstance(a, float) and isinstance(b, float):
            if abs(a - b) > tol:
                equal = False
        else:
            if a != b:
                equal = False

        if not equal:
            noMatch.append({
                prop: {
                    'src1': a,
                    'src2': b
                }
            })

    if not len(noMatch):
        noMatch = None

    return noMatch


def compare(srcpath1, srcpath2, max_px_diff=0, upsample=1, downsample=1,
            compare_masked=True, no_stderr=False, debug=False, flex_mode=False):
    with rasterio.open(srcpath1) as src1:
        with rasterio.open(srcpath2) as src2:

            count1 = src1.count
            count2 = src2.count
            compareAlpha = 1

            if flex_mode and [count1, count2].count(3) != 0:
                props = ['crs', 'driver', 'bounds', 'height', 'width', 'shape']
                if src1.count * src2.count != 12 or src1.count + src2.count != 7:
                    exception_raiser(
                        "In flex mode, %s and %s must 3 and 4, or 4 and 3 bands "
                        "respectively (received %s and %s)" % (
                            srcpath1, srcpath2, src1.count, src2.count), no_stderr)
            else:
                props = ['count', 'crs', 'dtypes', 'driver', 'bounds',
                         'height', 'width', 'shape', 'nodatavals']
            propCompare = compare_properties(src1, src2, props)

            if propCompare:
                exception_raiser(propCompare, no_stderr)

            if compare_masked and src1.count == 4 and not flex_mode:
                # create arrays for decimated reading
                masked_1 = make_fill_array(
                    src1.height, src1.width, downsample, src1.meta['dtype'])
                masked_2 = make_fill_array(
                    src2.height, src2.width, downsample, src2.meta['dtype'])

                src1.read(4, out=masked_1, masked=False)
                src2.read(4, out=masked_2, masked=False)
                compareAlpha = 0
                difference, aboveThreshold = array_compare(
                    masked_1, masked_2, 16, max_px_diff, debug)

                if aboveThreshold:
                    exception_raiser(
                        'Mask has %s pixels that vary by more than 16' % (difference), no_stderr)

            elif compare_masked and flex_mode:
                masked_1 = make_fill_array(
                    src1.height, src1.width, downsample, src1.meta['dtype'])
                masked_2 = make_fill_array(
                    src2.height, src2.width, downsample, src2.meta['dtype'])

                src1.read_masks(1, out=masked_1)
                src2.read_masks(1, out=masked_2)
                compareAlpha = 0

                difference, aboveThreshold = array_compare(
                    masked_1, masked_2, 16, max_px_diff, debug)

                if aboveThreshold:
                    exception_raiser(
                        'Mask has %s pixels that vary by more than 16' % (difference),
                        no_stderr)

            for bidx in range(1, count1 + compareAlpha):
                # create arrays for decimated reading
                band1 = make_fill_array(
                    src1.height, src1.width, downsample, src1.meta['dtype'])
                band2 = make_fill_array(
                    src2.height, src2.width, downsample, src2.meta['dtype'])

                src1.read(bidx, out=band1, masked=False)
                band1 = band1.astype(np.int16)

                src2.read(bidx, out=band2, masked=False)
                band2 = band2.astype(np.int16)

                if compare_masked and src1.count == 4:
                    band1[masked_1 != 255] = 0
                    band2[masked_1 != 255] = 0

                if upsample > 1:
                    toAff, frAff = affaux(upsample)
                    band1 = upsample_array(band1, upsample, frAff, toAff)
                    band2 = upsample_array(band2, upsample, frAff, toAff)

                difference, aboveThreshold = array_compare(
                    band1, band2, 16, max_px_diff, debug)

                if aboveThreshold:
                    exception_raiser('Band %s has %s pixels that vary by more than 16' % (
                        bidx, difference), no_stderr)

    click.echo("ok - %s is similar to within %s pixels of %s" %
               (srcpath1, max_px_diff, srcpath2))
