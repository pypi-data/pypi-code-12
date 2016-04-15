"""
This module implement a Upscale filter.
"""
from .interface import ImagineFilterInterface
from PIL import Image


class UpscaleFilter(ImagineFilterInterface):
    """
    Upscale filter
    """
    size = None

    def __init__(self, **kwargs):
        """
        :param kwargs: dict
        """
        if 'min' in kwargs and isinstance(kwargs['min'], list) and len(kwargs['min']) == 2:
            self.size = kwargs.get('min')
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

        if original_width < self.size[0] and original_height < self.size[1]:
            k = original_width / float(original_height)

            if original_width >= original_height:
                target_width = self.size[0]
                target_height = int(target_width / k)
            else:
                target_height = self.size[1]
                target_width = int(target_height * k)

            resource = resource.resize((target_width, target_height), Image.ANTIALIAS)

        return resource
