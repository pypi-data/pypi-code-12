"""
This module implement a filesystem storage adapter.
"""
import errno
import logging
import os
from flask import current_app
from .interface import ImagineAdapterInterface
from PIL import Image

LOGGER = logging.getLogger(__name__)


class ImagineFilesystemAdapter(ImagineAdapterInterface):
    """
    Filesystem storage adapter
    """
    source_folder = None
    cache_folder = None

    def __init__(self, **kwargs):
        """
        Init adapter
        :param kwargs: parameters
        :return:
        """
        if 'source_folder' in kwargs:
            self.source_folder = kwargs.pop('source_folder').strip('/')
        else:
            raise ValueError('Source folder does not set.')

        self.cache_folder = kwargs.pop('cache_folder', 'cache').strip('/')

    def get_item(self, path):
        """
        Get resource item
        :param path: string
        :return: Image
        """
        item_path = '%s/%s/%s' % (
                current_app.root_path,
                self.source_folder,
                path.strip('/')
            )

        if os.path.isfile(item_path):
            try:
                return Image.open(item_path)
            except IOError, e:
                LOGGER.warning('File not found on path "%s" with error: %s' % (item_path, unicode(e)))
                return False
        else:
            return False

    def create_cached_item(self, path, content):
        """
        Create cached resource item
        :param path: string
        :param content: Image
        :return:
        """
        if isinstance(content, Image.Image):
            item_path = '%s/%s/%s/%s' % (
                current_app.root_path,
                self.source_folder,
                self.cache_folder,
                path.strip('/')
            )
            self.make_dirs(item_path)

            content.save(item_path)

            if os.path.isfile(item_path):
                return '/%s/%s/%s' % (self.source_folder, self.cache_folder, path.strip('/'))
            else:  # pragma: no cover
                LOGGER.warning('File is not created on path: %s' % item_path)
                return False
        else:
            return False

    def get_cached_item(self, path):
        """
        Get cached resource item
        :param path: string
        :return:
        """
        item_path = '%s/%s/%s/%s' % (
                current_app.root_path,
                self.source_folder,
                self.cache_folder,
                path.strip('/')
            )

        if os.path.isfile(item_path):
            try:
                return Image.open(item_path)
            except IOError, e:  # pragma: no cover
                LOGGER.warning('Cached file not found on path "%s" with error: %s' % (item_path, unicode(e)))
                return False
        else:
            return False

    def check_cached_item(self, path):
        """
        Check for cached resource item exists
        :param path: string
        :return:
        """
        item_path = '%s/%s/%s/%s' % (
                current_app.root_path,
                self.source_folder,
                self.cache_folder,
                path.strip('/')
            )

        return os.path.isfile(item_path)

    def remove_cached_item(self, path):
        """
        Remove cached resource item
        :param path: string
        :return:
        """
        item_path = '%s/%s/%s/%s' % (
                current_app.root_path,
                self.source_folder,
                self.cache_folder,
                path.strip('/')
            )

        if os.path.isfile(item_path):
            os.remove(item_path)

        return True

    @staticmethod
    def make_dirs(path):
        """
        Create directories if not exist
        :param path: string
        :return:
        """
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as e:
            if e.errno != errno.EEXIST:
                LOGGER.error('Failed to create directory %s with error: %s' % (path, unicode(e)))
                raise
