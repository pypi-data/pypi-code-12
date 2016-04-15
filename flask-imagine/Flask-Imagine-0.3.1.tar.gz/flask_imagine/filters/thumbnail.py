"""
This module implement a Thumbnail filter.
"""
from PIL import Image
from .interface import ImagineFilterInterface


class ThumbnailFilter(ImagineFilterInterface):
    """
    Thumbnail filter
    """
    modes = ['inset', 'outbound']
    mode = 'inset'
    width = 0
    height = 0

    def __init__(self, **kwargs):
        """
        Filter initialization
        :param kwargs: parameters
        """
        if 'mode' in kwargs and kwargs['mode'] in self.modes:
            self.mode = kwargs.pop('mode')

        if 'size' in kwargs and isinstance(kwargs['size'], list) and len(kwargs['size']) == 2:
            size = kwargs.pop('size', [0, 0])
            self.width = size[0]
            self.height = size[1]
        else:
            raise ValueError('Thumbnail size is not set.')

    def apply(self, resource):
        """
        Apply filter to resource
        :param resource: Image
        :return: Image
        """
        if not isinstance(resource, Image.Image):
            raise ValueError('Unknown resource format')

        original_width, original_height = resource.size

        if self.mode == 'outbound':
            target_width, target_height = self.outbound_sizes(original_width, original_height, self.width, self.height)
            resource = resource.resize((target_width, target_height), Image.ANTIALIAS)

            crop_sizes = self.crop_sizes(target_width, target_height, self.width, self.height)
            resource = resource.crop(crop_sizes)
        else:
            target_width, target_height = self.inset_sizes(original_width, original_height, self.width, self.height)
            resource = resource.resize((target_width, target_height), Image.ANTIALIAS)

        return resource

    @classmethod
    def inset_sizes(cls, original_width, original_height, target_width, target_height):
        """
        Calculate new image sizes for inset mode
        :param original_width: int
        :param original_height: int
        :param target_width: int
        :param target_height: int
        :return: tuple(int, int)
        """
        if target_width >= original_width and target_height >= original_height:
            target_width = float(original_width)
            target_height = original_height

        elif target_width <= original_width and target_height >= original_height:
            k = original_width / float(target_width)
            target_height = int(original_height / k)

        elif target_width >= original_width and target_height <= original_height:
            k = original_height / float(target_height)
            target_width = int(original_width / k)

        elif target_width < original_width and target_height < original_height:
            k = original_width / float(original_height)
            k_w = original_width / float(target_width)
            k_h = original_height / float(target_height)

            if k_w >= k_h:
                target_height = int(target_width / k)
            else:
                target_width = int(target_height * k)

        return target_width, target_height

    @classmethod
    def outbound_sizes(cls, original_width, original_height, target_width, target_height):
        """
        Calculate new image sizes for outbound mode
        :param original_width: int
        :param original_height: int
        :param target_width: int
        :param target_height: int
        :return: tuple(int, int)
        """
        if target_width <= original_width and target_height <= original_height:
            k = original_width / float(original_height)
            k_w = original_width / float(target_width)
            k_h = original_height / float(target_height)

            if k_w > k_h:
                target_width = int(target_height * k)
            else:
                target_height = int(target_width / k)
        else:
            target_width = original_width
            target_height = original_height

        return target_width, target_height

    @classmethod
    def crop_sizes(cls, original_width, original_height, target_width, target_height):
        """
        Calculate crop parameters for outbound mode
        :param original_width: int
        :param original_height: int
        :param target_width: int
        :param target_height: int
        :return: tuple(int, int, int, int)
        """
        if target_width < original_width:
            left = abs(original_width - target_width) / 2
            right = left + target_width
        else:
            left = 0
            right = original_width
        if target_height < original_height:
            upper = abs(original_height - target_height) / 2
            lower = upper + target_height
        else:
            upper = 0
            lower = original_height

        return left, upper, right, lower
