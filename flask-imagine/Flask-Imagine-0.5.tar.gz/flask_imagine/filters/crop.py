"""
This module implement a Crop filter.
"""
from .interface import ImagineFilterInterface
from PIL import Image


class CropFilter(ImagineFilterInterface):
    """
    Crop filter
    """
    start = None
    size = None

    def __init__(self, start, size):
        """
        :param start: list
        :param size: list
        """
        if isinstance(start, list) and len(start) == 2:
            self.start = start
        else:
            raise ValueError('Unknown start position.')

        if isinstance(size, list) and len(size) == 2:
            self.size = size
        else:
            raise ValueError('Unknown image size.')

    def apply(self, resource):
        """
        Apply filter to resource
        :param resource: Image
        :return: Image
        """
        if not isinstance(resource, Image.Image):
            raise ValueError('Unknown resource format')

        original_width, original_height = resource.size

        if self.start[0] < original_width or self.start[1] < original_height:
            left = self.start[0]
            upper = self.start[1]
        else:
            left = 0
            upper = 0

        right = self.start[0] + self.size[0]
        lower = self.start[1] + self.size[1]

        resource_format = resource.format
        resource = resource.crop(
            (
                left,
                upper,
                right if right < original_width else original_width,
                lower if lower < original_height else original_height
            )
        )
        resource.format = resource_format

        return resource
