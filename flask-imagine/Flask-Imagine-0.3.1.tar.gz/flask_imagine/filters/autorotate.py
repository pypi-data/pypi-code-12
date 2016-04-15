"""
This module implement a Autorotate filter.
"""
from PIL import Image
from .interface import ImagineFilterInterface


class AutorotateFilter(ImagineFilterInterface):
    """
    Autorotate filter
    """
    def apply(self, resource):
        """
        Apply filter to resource
        :param resource: Image
        :return: Image
        """
        if not isinstance(resource, Image.Image):
            raise ValueError('Unknown resource format')

        if hasattr(resource, '_getexif'):
            exif = getattr(resource, '_getexif')()
            if not exif:
                return resource

            orientation_key = 274  # cf ExifTags
            if orientation_key in exif:
                orientation = exif[orientation_key]

                rotate_values = {
                    3: 180,
                    6: 270,
                    8: 90
                }

                if orientation in rotate_values:
                    resource = resource.rotate(rotate_values[orientation])

        return resource
