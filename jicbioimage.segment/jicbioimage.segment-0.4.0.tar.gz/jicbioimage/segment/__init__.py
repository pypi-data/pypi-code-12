"""Module containing image segmentation functions.

Example usage:

>>> import numpy as np
>>> from jicbioimage.core.image import Image
>>> ar = np.array([[1, 1, 0, 0, 0],
...                [1, 1, 0, 0, 0],
...                [0, 0, 0, 0, 0],
...                [0, 0, 2, 2, 2],
...                [0, 0, 2, 2, 2]], dtype=np.uint8)
...
>>> im = Image.from_array(ar)
>>> connected_components(im)  # doctest: +NORMALIZE_WHITESPACE
SegmentedImage([[3, 3, 1, 1, 1],
                [3, 3, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [1, 1, 2, 2, 2],
                [1, 1, 2, 2, 2]])
>>> connected_components(im, background=0)  # doctest: +NORMALIZE_WHITESPACE
SegmentedImage([[2, 2, 0, 0, 0],
                [2, 2, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1],
                [0, 0, 1, 1, 1]])
>>> segmentation = connected_components(im, background=0)
>>> segmentation.history
['Created image from array', 'Applied connected_components transform']

"""

import numpy as np
import scipy.ndimage as nd
import skimage.measure
import skimage.morphology

from jicbioimage.core.image import Image
from jicbioimage.core.transform import transformation
from jicbioimage.core.util.array import pretty_color_array, unique_color_array

__version__ = "0.4.0"


class Region(np.ndarray):
    """Class representing a region of interest in an image.

    The :class:`jicbioimage.core.region.Region` class is a subclass of
    numpy.ndarray.

    However, note that it will compress any data given to it to boolean.

    >>> import numpy as np
    >>> ar = np.array([-1, 0, 1, 2])
    >>> Region(ar)
    Region([ True, False,  True,  True], dtype=bool)

    To select an particular element use the
    :func:`jicbioimage.core.region.Region.select_from_array` class method.

    >>> Region.select_from_array(ar, identifier=2)
    Region([False, False, False,  True], dtype=bool)

    """

    def __new__(cls, input_array):
        obj = np.asarray(input_array).view(cls)
        return obj.astype(bool)

    @classmethod
    def select_from_array(cls, array, identifier):
        """Return a region from a numpy array.

        :param array: :class:`numpy.ndarray`
        :param identifier: value representing the region to select in the array
        :returns: :class:`jicbioimage.core.region.Region`
        """

        base_array = np.zeros(array.shape)
        array_coords = np.where(array == identifier)
        base_array[array_coords] = 1

        return cls(base_array)

    @property
    def inner(self):
        """Region formed by taking non-border elements.

        :returns: :class:`jicbioimage.core.region.Region`
        """

        inner_array = nd.morphology.binary_erosion(self)
        return Region(inner_array)

    @property
    def border(self):
        """Region formed by taking border elements.

        :returns: :class:`jicbioimage.core.region.Region`
        """

        border_array = self - self.inner
        return Region(border_array)

    @property
    def convex_hull(self):
        """Region representing the convex hull.

        :returns: :class:`jicbioimage.core.region.Region`
        """
        hull_array = skimage.morphology.convex_hull_image(self)
        return Region(hull_array)

    @property
    def area(self):
        """Number of non-zero elements.

        :returns: int
        """
        return np.count_nonzero(self)

    @property
    def index_arrays(self):
        """All nonzero elements as a pair of arrays."""
        return np.where(self == True)

    @property
    def points(self):
        """Region as a list of points."""
        return list(zip(*self.index_arrays))

    @property
    def perimeter(self):
        """Return the perimiter.

        :returns: int
        """
        return self.border.area

    def dilate(self, iterations=1):
        """Return a dilated region.

        :param iterations: number of iterations to use in dilation
        :returns: :class:`jicbioimage.core.region.Region`
        """
        dilated_array = nd.morphology.binary_dilation(self,
                                                      iterations=iterations)
        return Region(dilated_array)

    @property
    def centroid(self):
        """Return centroid as (y, x) tuple."""
        return tuple([np.mean(ia) for ia in self.index_arrays])


class SegmentedImage(Image):
    """Class representing the results of applying a segmentation to an image.

    Each unique pixel value represents a different region of the segmentation.
    0 represents background and positive integers represent the different
    regions.
    """

    @property
    def identifiers(self):
        """Return a set of unique identifiers in the segmented image."""

        return set(np.unique(self)) - set([0])

    @property
    def number_of_segments(self):
        """Return the number of segments present in the segmented image."""

        return len(self.identifiers)

    def region_by_identifier(self, identifier):
        """Return region of interest corresponding to the supplied identifier.

        :param identifier: integer corresponding to the segment of interest
        :returns: `jicbioimage.core.region.Region`
        """

        if identifier < 0:
            raise(ValueError("Identifier must be a positive integer."))

        if not np.equal(np.mod(identifier, 1), 0):
            raise(ValueError("Identifier must be a positive integer."))

        if identifier == 0:
            raise(ValueError("0 represents the background."))

        return Region.select_from_array(self, identifier)

    @property
    def background(self):
        """Return the segmented image background.

        In other words the region with pixel values 0.

        :returns: `jicbioimage.core.region.Region`
        """

        return Region.select_from_array(self, 0)

    @property
    def pretty_color_image(self):
        """Return segmentation as a pretty color image.

        :returns: `jicbioimage.core.image.Image`
        """
        return Image.from_array(pretty_color_array(self))

    @property
    def unique_color_image(self):
        """Return segmentation as a unique color image.

        :returns: `jicbioimage.core.image.Image`
        """
        return Image.from_array(unique_color_array(self))

    def png(self, width=None):
        """Return png string of image.

        :param width: integer specifying the desired width
        :returns: png as a string
        """
        return self.pretty_color_image.png(width)

    def remove_region(self, identifier):
        """Remove region from the segmentation.

        :param identifier: region identifier
        """
        region = self.region_by_identifier(identifier)
        self[region] = 0

    def merge_regions(self, id1, id2):
        """Merge two regions into one.

        The merged region will take on the id1 identifier.

        :param id1: region 1 identifier
        :param id2: region 2 identifier
        """
        region2 = self.region_by_identifier(id2)
        self[region2] = id1


@transformation
def connected_components(image, connectivity=2, background=None):
    """Return :class:`jicbioimage.core.image.SegmentedImage`.

    :param image: input :class:`jicbioimage.core.image.Image`
    :param connectivity: maximum number of orthagonal hops to consider a
                         pixel/voxel as a neighbor
    :param background: consider all pixels with this value (int) as background
    :returns: :class:`jicbioimage.core.image.SegmentedImage`
    """
    # Work around skimage.measure.label behaviour in version 0.12 and higher
    # treats all 0 pixels as background even if "background" argument is set
    # to None.
    if background is None:
        image[np.where(image == 0)] = np.max(image) + 1

    ar = skimage.measure.label(image, connectivity=connectivity,
                               background=background)

    # The :class:`jicbioimage.core.image.SegmentedImage` assumes that zero is
    # background.  So we need to change the identifier of any pixels that are
    # marked as zero if there is no background in the input image.
    if background is None:
        ar[np.where(ar == 0)] = np.max(ar) + 1
    else:
        if np.min(ar) == -1:
            # Work around skimage.measure.label behaviour pre version 0.12.
            # Pre version 0.12 the background in skimage was labeled -1 and the
            # first component was labelled with 0.
            # The jicbioimage.core.image.SegmentedImage assumes that the
            # background is labelled 0.
            ar[np.where(ar == 0)] = np.max(ar) + 1
            ar[np.where(ar == -1)] = 0

    segmentation = SegmentedImage.from_array(ar)
    return segmentation


@transformation
def watershed_with_seeds(image, seeds, mask=None):
    """Return :class:`jicbioimage.core.image.SegmentedImage`.

    :param image: input :class:`jicbioimage.core.image.Image`
    :param seeds: numpy.ndarray of same shape as image,
                  each seed needs to be a unique integer
    :param mask: bool numpy.ndarray of same shape as image,
                 only regions that are marked as True will be labelled
    :returns: :class:`jicbioimage.core.image.SegmentedImage`
    """
    ar = skimage.morphology.watershed(-image, seeds, mask=mask)
    segmentation = SegmentedImage.from_array(ar)
    return segmentation
