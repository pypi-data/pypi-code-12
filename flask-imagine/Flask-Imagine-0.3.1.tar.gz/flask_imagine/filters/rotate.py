"""
This module implement a Rotate filter.
"""
from PIL import Image
from .interface import ImagineFilterInterface


class RotateFilter(ImagineFilterInterface):
    """
    Rotate filter
    """
    angle = None

    def __init__(self, **kwargs):
        """
        :param kwargs: dict
        """
        if 'angle' in kwargs and isinstance(kwargs['angle'], (int, float)):
            self.angle = kwargs.get('angle', 0)
        else:
            raise ValueError('Unsupported angle format or angle doesn\'t set')

    def apply(self, resource):
        """
        Apply filter to resource
        :param resource: Image
        :return: Image
        """
        if not isinstance(resource, Image.Image):
            raise ValueError('Unknown resource format')

        resource = resource.rotate(self.angle, expand=True)

        return resource
