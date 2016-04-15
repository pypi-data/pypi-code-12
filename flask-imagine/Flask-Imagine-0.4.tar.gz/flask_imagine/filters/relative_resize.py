"""
This module implement a Relative resize filter.
"""
from .interface import ImagineFilterInterface
from PIL import Image


class RelativeResizeFilter(ImagineFilterInterface):
    """
    Relative resize filter
    """
    methods = ['heighten', 'widen', 'increase', 'decrease', 'scale']
    method = None
    value = None

    def __init__(self, **kwargs):
        """
        :param kwargs: dict
        """
        for method in self.methods:
            if method in kwargs:
                self.method = method

        if not self.method:
            raise ValueError('Unknown method')

        if self.method == 'scale':
            try:
                self.value = float(kwargs[self.method])
            except Exception, e:
                raise ValueError('Wrong value type: %s' % unicode(e))
        else:
            try:
                self.value = int(kwargs[self.method])
            except Exception, e:
                raise ValueError('Wrong value type: %s' % unicode(e))

    def apply(self, resource):
        """
        :param resource: Image
        :return: Image
        """
        if isinstance(resource, Image.Image):
            return getattr(self, '_' + self.method)(resource)
        else:
            raise ValueError('Unsupported resource format: %s' % str(type(resource)))

    def _heighten(self, resource):
        """
        Change image size by height
        :param resource: Image
        :return: Image
        """
        original_width, original_height = resource.size

        target_height = self.value
        target_width = int((float(target_height) / original_height) * original_width)

        resource = resource.resize((target_width, target_height), Image.ANTIALIAS)

        return resource

    def _widen(self, resource):
        """
        Change image size by width
        :param resource: Image
        :return: Image
        """
        original_width, original_height = resource.size

        target_width = self.value
        target_height = int((float(target_width) / original_width) * original_height)

        resource = resource.resize((target_width, target_height), Image.ANTIALIAS)

        return resource

    def _increase(self, resource):
        """
        Increase image size
        :param resource: Image
        :return: Image
        """
        original_width, original_height = resource.size

        target_width = original_width + self.value
        target_height = original_height + self.value

        resource = resource.resize((target_width, target_height), Image.ANTIALIAS)

        return resource

    def _decrease(self, resource):
        """
        Decrease image size
        :param resource:
        :return:
        """
        original_width, original_height = resource.size

        if original_width > self.value and original_height > self.value:
            target_width = original_width - self.value
            target_height = original_height - self.value

            resource = resource.resize((target_width, target_height), Image.ANTIALIAS)

            return resource
        else:
            raise ValueError('Image dimensions less than or equal to filter value.')

    def _scale(self, resource):
        """
        Scale image
        :param resource: Image
        :return: Image
        """
        original_width, original_height = resource.size

        target_width = int(round(original_width * self.value))
        target_height = int(round(original_height * self.value))

        resource_format = resource.format
        resource = resource.resize((target_width, target_height), Image.ANTIALIAS)
        resource.format = resource_format

        return resource
