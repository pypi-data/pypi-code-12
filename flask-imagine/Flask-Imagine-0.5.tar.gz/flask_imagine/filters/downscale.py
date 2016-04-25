"""
This module implement a downscale filter.
"""
from __future__ import division
from .interface import ImagineFilterInterface
from PIL import Image


class DownscaleFilter(ImagineFilterInterface):
    """
    Downscale filter
    """
    size = None

    def __init__(self, **kwargs):
        """
        :param kwargs: dict
        """
        if 'max' in kwargs and isinstance(kwargs['max'], list) and len(kwargs['max']) == 2:
            self.size = kwargs.get('max')
        else:
            raise ValueError('Unsupported configuration')

    def apply(self, resource):
        """
        Apply filter to resource.
        :param resource: Image
        :return: Image
        """
        if not isinstance(resource, Image.Image):
            raise ValueError('Unsupported resource format: %s' % str(type(resource)))

        original_width, original_height = resource.size

        if original_width > self.size[0] or original_height > self.size[1]:
            k = original_width / original_height

            if original_width >= original_height:
                target_width = self.size[0]
                target_height = int(target_width / k)
            else:
                target_height = self.size[1]
                target_width = int(target_height * k)

            resource_format = resource.format
            resource = resource.resize((target_width, target_height), Image.ANTIALIAS)
            resource.format = resource_format

        return resource
