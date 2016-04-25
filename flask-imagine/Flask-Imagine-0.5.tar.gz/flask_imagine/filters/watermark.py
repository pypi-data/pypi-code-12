"""
This module implement a Watermark filter.
"""
from __future__ import unicode_literals, division
import os
from flask import current_app

from .interface import ImagineFilterInterface
from PIL import Image, ImageEnhance


class WatermarkFilter(ImagineFilterInterface):
    """
    Watermark filter
    """
    positions = ['top_left', 'top', 'top_right', 'left', 'center', 'right', 'bottom_left', 'bottom', 'bottom_right']

    image_path = None
    image = None
    size = None
    position = None
    opacity = None

    def __init__(self, **kwargs):
        """
        :param kwargs: dict
        """
        if 'image' in kwargs:
            self.image_path = os.path.normpath(str(kwargs['image']))
        else:
            raise ValueError('Watermark image path doesn\'t set.')

        if 'size' in kwargs:
            try:
                self.size = float(kwargs.get('size'))
                assert 0 <= self.size <= 1
            except Exception as err:
                raise ValueError('Unsupported size format: %s' % str(err))
        else:
            raise ValueError('Watermark size doesn\'t set.')

        if 'position' in kwargs:
            if kwargs['position'] in self.positions:
                self.position = kwargs.get('position')
            else:
                raise ValueError('Unsupported watermark position: %s' % kwargs.get('position'))
        else:
            raise ValueError('Watermark position doesn\'t set.')

        if 'opacity' in kwargs:
            try:
                self.opacity = float(kwargs.get('opacity', 0.3))
                assert 0 <= self.opacity <= 1
            except Exception as err:
                raise ValueError('Unsupported opacity format: %s' % str(err))
        else:
            self.opacity = 0.3

    def apply(self, resource):
        """
        Apply filter to resource
        :param resource: Image.Image
        :return: Image.Image
        """
        if not isinstance(resource, Image.Image):
            raise ValueError('Unknown resource format')

        resource_format = resource.format
        if resource.mode != 'RGBA':  # pragma: no cover
            resource = resource.convert('RGBA')

        layer = Image.new('RGBA', resource.size, (0, 0, 0, 0))
        image, left, upper = getattr(self, '_' + self.position + '_position')(resource)
        layer.paste(image, (left, upper))

        image = Image.composite(layer, resource, layer)
        image.format = resource_format

        return image

    def _top_left_position(self, resource):
        """
        Place watermark to top left position
        :param resource: Image.Image
        :return: Image.Image
        """
        image = self._get_scaled_image(resource)

        return image, 0, 0

    def _top_position(self, resource):
        """
        Place watermark to top position
        :param resource: Image.Image
        :return: Image.Image
        """
        image = self._get_scaled_image(resource)

        left = int(round(resource.size[0] // 2 - image.size[0] // 2))
        upper = 0

        return image, left, upper

    def _top_right_position(self, resource):
        """
        Place watermark to top right position
        :param resource: Image.Image
        :return: Image.Image
        """
        image = self._get_scaled_image(resource)

        left = int(round(resource.size[0] - image.size[0]))
        upper = 0

        return image, left, upper

    def _left_position(self, resource):
        """
        Place watermark to left position
        :param resource: Image.Image
        :return: Image.Image
        """
        image = self._get_scaled_image(resource)

        left = 0
        upper = int(round(resource.size[1] // 2 - image.size[1] // 2))

        return image, left, upper

    def _center_position(self, resource):
        """
        Place watermark to center position
        :param resource: Image.Image
        :return: Image.Image
        """
        image = self._get_scaled_image(resource)

        left = int(round(resource.size[0] // 2 - image.size[0] // 2))
        upper = int(round(resource.size[1] // 2 - image.size[1] // 2))

        return image, left, upper

    def _right_position(self, resource):
        """
        Place watermark to right position
        :param resource: Image.Image
        :return: Image.Image
        """
        image = self._get_scaled_image(resource)

        left = int(round(resource.size[0] - image.size[0]))
        upper = int(round(resource.size[1] // 2 - image.size[1] // 2))

        return image, left, upper

    def _bottom_left_position(self, resource):
        """
        Place watermark to bottom left position
        :param resource: Image.Image
        :return: Image.Image
        """
        image = self._get_scaled_image(resource)

        left = 0
        upper = int(round(resource.size[1] - image.size[1]))

        return image, left, upper

    def _bottom_position(self, resource):
        """
        Place watermark to bottom position
        :param resource: Image.Image
        :return: Image.Image
        """
        image = self._get_scaled_image(resource)

        left = int(round(resource.size[0] // 2 - image.size[0] // 2))
        upper = int(round(resource.size[1] - image.size[1]))

        return image, left, upper

    def _bottom_right_position(self, resource):
        """
        Place watermark to bottom right position
        :param resource: Image.Image
        :return: Image.Image
        """
        image = self._get_scaled_image(resource)

        left = int(round(resource.size[0] - image.size[0]))
        upper = int(round(resource.size[1] - image.size[1]))

        return image, left, upper

    def _get_image(self):
        """
        Prepare watermark image
        :return: Image.Image
        """
        if self.image is None:
            image_path = '%s/%s' % (current_app.static_folder, os.path.normpath(self.image_path))
            try:
                self.image = Image.open(image_path)
                self._reduce_opacity()
            except Exception as err:
                raise ValueError('Unsupported watermark format: %s' % str(err))

        return self.image

    def _reduce_opacity(self):
        """
        Reduce opacity for watermark image.
        """
        if self.image.mode != 'RGBA':
            image = self.image.convert('RGBA')
        else:
            image = self.image.copy()

        alpha = image.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(self.opacity)
        image.putalpha(alpha)

        self.image = image

    def _get_scaled_image(self, resource):
        """
        Get scaled watermark image
        :param resource: Image.Image
        :return: Image.Image
        """
        image = self._get_image()
        original_width, original_height = resource.size

        k = image.size[0] / float(image.size[1])

        if image.size[0] >= image.size[1]:
            target_width = int(original_width * self.size)
            target_height = int(target_width / k)
        else:
            target_height = int(original_height * self.size)
            target_width = int(target_height * k)

        image = image.resize((target_width, target_height), Image.ANTIALIAS)

        return image

