# -*- encoding: utf-8 -*-
import cffi
import numpy as np

from .utils import shared_lib, full_filename

ffi = cffi.FFI()
ffi.cdef(open(full_filename("ims.h")).read())
_ims = ffi.dlopen(full_filename(shared_lib("ims_cffi")))

_has_numpy = True
_dtypes = {'f': np.float32, 'd': np.float64}
_full_types = {'f': 'float', 'd': 'double'}

def _as_buffer(array, numtype):
    return np.asarray(array, dtype=_dtypes[numtype])

class _cffi_buffer(object):
    def __init__(self, n, numtype):
        self.buf = np.zeros(n, dtype=_dtypes[numtype])
        self.ptr = ffi.cast('void *', self.buf.__array_interface__['data'][0])

    def python_data(self):
        return self.buf

def _raise_ims_exception():
    raise Exception(ffi.string(_ims.ims_strerror()))

def _raise_ims_exception_if_null(arg):
    if arg == ffi.NULL:
        _raise_ims_exception()

class ImzbReader(object):
    """
    Class for reading .imzb format.

    WARNING: the format is not standardized and might change in the future without any backward compatibility considerations; use it at your own risk!

    .imzb format is optimized for very fast m/z-image queries.

    ImzML files can be converted to it using 'ims convert' tool that
    must be compiled from source: https://github.com/alexandrovteam/ims-cpp
    """
    def __init__(self, filename):
        """
        Open .imzb file for reading
        """
        self._filename = filename
        r = _ims.imzb_reader_new(filename)
        _raise_ims_exception_if_null(r)
        self._reader = ffi.gc(r, _ims.imzb_reader_free)

    @property
    def height(self):
        """
        Image height
        """
        return _ims.imzb_reader_height(self._reader)

    @property
    def width(self):
        """
        Image width
        """
        return _ims.imzb_reader_width(self._reader)

    @property
    def min_mz(self):
        """
        Minimal m/z value
        """
        return _ims.imzb_reader_min_mz(self._reader)

    @property
    def max_mz(self):
        """
        Maximal m/z value
        """
        return _ims.imzb_reader_max_mz(self._reader)

    def get_mz_image(self, mz, ppm):
        """
        Read m/z-image formed from peaks within mz × (1 ± 10 :sup:`-6` × ppm) window.

        Pixels that were not scanned have intensity set to -1.
        """
        data = np.zeros(self.height * self.width, dtype=np.float32)
        read_func = _ims.imzb_reader_image
        ret = read_func(self._reader, ffi.cast("double", mz), ffi.cast("double", ppm),
                        ffi.from_buffer(data))
        if ret < 0:
            _raise_ims_exception()
        return data.reshape((self.height, self.width))

def measure_of_chaos(im, nlevels):
    """
    Compute a measure for the spatial chaos in given image using the level sets method.

    :param im: 2d array
    :param nlevels: how many levels to use (maximum of 32 in this implementation)
    :type nlevels: int
    """
    assert nlevels > 0
    if nlevels > 32:
        raise RuntimeError("maximum of 32 levels is supported")
    im = np.asarray(im, dtype=np.float32)
    return _ims.measure_of_chaos_f(ffi.from_buffer(im),
                                   ffi.cast("int", im.shape[1]),
                                   ffi.cast("int", im.shape[0]),
                                   ffi.cast("int", nlevels))

def _compute_metric(metric, images_flat, theor_iso_intensities):
    assert len(images_flat) == len(theor_iso_intensities)
    assert all(np.shape(im) == np.shape(images_flat[0]) for im in images_flat)
    assert all(len(np.shape(im)) == 1 for im in images_flat)
    assert all(intensity >= 0 for intensity in theor_iso_intensities)

    n = len(images_flat)
    images = ffi.new("float*[]", n)
    for i in range(n):
        images[i] = ffi.from_buffer(_as_buffer(images_flat[i], 'f'))
    abundances = _as_buffer(theor_iso_intensities, 'd')

    return metric(images,
                  ffi.cast("int", n),
                  ffi.cast("int", len(images_flat[0])),
                  ffi.cast("int", 1),
                  ffi.from_buffer(abundances))

def isotope_pattern_match(images_flat, theor_iso_intensities):
    """
    Measures similarity between total isotope image intensities and the theoretical pattern.

    :param images_flat: list of flattened isotope images
    :param theor_iso_intensities: list of the corresponding theoretical isotope abundances
    :rtype: float
    """
    return _compute_metric(_ims.pattern_match_f, images_flat, theor_iso_intensities)

def isotope_image_correlation(images_flat, weights=None):
    """
    Calculates weighted average of correlations between principal peak image and the rest.

    :param images_flat: list of flattened isotope images
    :param weights: If provided, must be one element shorter than :code:`images_flat` list.
                    Default value of :code:`None` corresponds to equal weights.
    :rtype: float
    """
    if weights is None:
        weights = np.ones(len(images_flat))
    else:
        weights = np.concatenate(([1.0], weights))
    return _compute_metric(_ims.iso_img_correlation_f, images_flat, weights)
