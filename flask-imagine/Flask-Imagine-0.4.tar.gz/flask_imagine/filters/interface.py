"""
This module implement a filter interface.
"""


class ImagineFilterInterface(object):
    """
    Filter interface
    """
    def apply(self, resource):
        """
        Apply filter to resource
        :param resource: Image
        :return: Image
        """
        raise NotImplementedError()
