"""
This module implement a storage adapter interface.
"""


class ImagineAdapterInterface(object):
    """
    Storage adapter interface
    """
    def get_item(self, path):
        """
        Get resource item
        :param path: string
        :return: Image
        """
        raise NotImplementedError()

    def create_cached_item(self, path, content):
        """
        Create cached resource item
        :param path: string
        :param content: Image
        :return:
        """
        raise NotImplementedError()

    def get_cached_item(self, path):
        """
        Get cached resource item
        :param path: string
        :return:
        """
        raise NotImplementedError()

    def check_cached_item(self, path):
        """
        Check for cached resource item exists
        :param path: string
        :return:
        """
        raise NotImplementedError()

    def remove_cached_item(self, path):
        """
        Remove cached resource item
        :param path: string
        :return:
        """
        raise NotImplementedError()
