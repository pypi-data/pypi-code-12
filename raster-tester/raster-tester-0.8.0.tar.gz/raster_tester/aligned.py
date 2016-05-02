#!/usr/bin/env python
import rasterio

def tiled(sources, equal_blocks=True):
    """ Tests if raster sources have the same tiling
    optionally assert that their block sizes are equal (default: True)
    """
    blocksize = None
    with rasterio.drivers():
        for source in sources:
            with rasterio.open(source) as src:

                if not src.profile['tiled']:
                    return (False, "Source(s) are not internally tiled")

                if equal_blocks:
                    this_blocksize = (src.profile['blockxsize'],
                                      src.profile['blockysize'])
                    if blocksize:
                        if blocksize != this_blocksize:
                            return (False, "Blocksizes are not equal")
                    else:
                        blocksize = this_blocksize

    return (True, "Tiling checks out")


def aligned(sources):
    """ Tests if raster sources are aligned
    i.e. have the same transform and shape
    (and by extension the same resolution and extent)
    """
    atransform = None
    shape = None
    with rasterio.drivers():
        for source in sources:
            with rasterio.open(source) as src:

                if atransform:
                    if src.affine != atransform:
                        return (False, "Affine transforms are not aligned")
                else:
                    atransform = src.affine

                if shape:
                    if src.shape != shape:
                        return (False, "Sources have different shape")
                else:
                    shape = src.shape

    return (True, "Sources have the same shape and transform")
