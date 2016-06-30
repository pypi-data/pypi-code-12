"""
This file provides the ShapesLibrary class needed for SPADE, along with some
ready-to-use shapes libraries.
"""

from os.path import dirname, join
import warnings

import numpy as np
from scipy.ndimage.morphology import binary_dilation
from scipy.ndimage import generate_binary_structure


class ShapesLibrary(np.ndarray):
    """Shapes library class for SPADE"""

    # TODO: make size restriction easier. How? I don't know.
    def __new__(cls, input_array, name="Unknown", sort=True):
        if sort:
            input_array = np.array(sorted(input_array, key=np.sum), bool)
        elif type(input_array) != np.ndarray:
            input_array = np.asarray(input_array, bool)

        if input_array.ndim != 3 or input_array.shape[1] != \
                input_array.shape[2]:
            raise TypeError('Input array must be in the shape '
                            'number of shapes x grid_size x grid_size')

        obj = input_array.view(cls)
        obj.name = name
        obj.surfaces = get_surfaces(input_array)
        obj.rings = get_rings(input_array)
        obj.grid_size = input_array.shape[-1]
        obj.shape_start = start_dict(obj.surfaces)

        obj.half_shape_size = obj.grid_size // 2
        obj.image_extension_size = obj.half_shape_size + 1

        if not input_array[:, obj.half_shape_size, obj.half_shape_size].all():
            warnings.warn("At least one shape doesn't include the central "
                          "grid pixel. This may cause weird behaviour.")

        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.name = getattr(obj, 'name', None)
        self.surfaces = getattr(obj, 'surfaces', None)
        self.rings = getattr(obj, 'rings', None)
        self.grid_size = getattr(obj, 'grid_size', None)
        self.shape_start = getattr(obj, 'shape_start', None)
        self.image_extension_size = getattr(obj, 'image_extension_size', None)
        self.half_shape_size = getattr(obj, 'half_shape_size', None)

        # def update(self):
        #     shapes_array = np.asarray(self)
        #     self.surfaces = get_surfaces(shapes_array)
        #     self.rings = get_rings(shapes_array)
        #     self.shape_start = start_dict(self.surfaces)


def get_surfaces(array):
    return array.sum(axis=tuple(np.arange(1, array.ndim)))


def start_dict(array):
    return {k: np.searchsorted(array, k) for k in np.unique(array)}


def get_rings(array, connectivity=None):
    if not connectivity:
        connectivity = array.ndim
    structuring_element = generate_binary_structure(array.ndim, connectivity)
    structuring_element[[0, -1]] = 0
    padded_array = np.pad(array, 1, 'constant')[1:-1]
    rings = np.logical_xor(
        binary_dilation(padded_array, structuring_element), padded_array)
    return rings


local_dir = dirname(__file__)
potatoids_5x5_array = np.load(join(local_dir,
                                   'potatoids_5x5.npz'))['arr_0.npy']
potatoids_5x5__smallest_1_pix = ShapesLibrary(potatoids_5x5_array,
                                              name='Potatoids 5x5, 1 to 25px',
                                              sort=False)
potatoids_5x5__smallest_2_pix = ShapesLibrary(potatoids_5x5_array[1:],
                                              name='Potatoids 5x5, 2 to 25px',
                                              sort=False)
potatoids_5x5__smallest_3_pix = ShapesLibrary(potatoids_5x5_array[3:],
                                              name='Potatoids 5x5, 3 to 25px',
                                              sort=False)
potatoids_5x5__smallest_4_pix = ShapesLibrary(potatoids_5x5_array[7:],
                                              name='Potatoids 5x5, 4 to 25px',
                                              sort=False)

potatoids_3x3_array = np.load(join(local_dir,
                                   'potatoids_3x3.npz'))['arr_0.npy']
potatoids_3x3__smallest_1_pix = ShapesLibrary(potatoids_3x3_array,
                                              name='Potatoids 3x3, 1 to 9px',
                                              sort=False)
potatoids_3x3__smallest_2_pix = ShapesLibrary(potatoids_3x3_array[1:],
                                              name='Potatoids 3x3, 2 to 9px',
                                              sort=False)
potatoids_3x3__smallest_3_pix = ShapesLibrary(potatoids_3x3_array[3:],
                                              name='Potatoids 3x3, 3 to 9px',
                                              sort=False)
potatoids_3x3__smallest_4_pix = ShapesLibrary(potatoids_3x3_array[7:],
                                              name='Potatoids 3x3, 4 to 9px',
                                              sort=False)

potatoids_5x5 = potatoids_5x5__smallest_3_pix
potatoids_3x3 = potatoids_3x3__smallest_3_pix
