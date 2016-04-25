"""
This module implement a filesystem storage adapter.
"""
from __future__ import unicode_literals
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
        Init _adapter
        :param kwargs: parameters
        :return:
        """
        self.source_folder = kwargs.get('source_folder', '').strip('/')
        self.cache_folder = kwargs.get('cache_folder', 'cache').strip('/')

    def get_item(self, path):
        """
        Get resource item
        :param path: string
        :return: PIL.Image
        """
        if self.source_folder:
            item_path = '%s/%s/%s' % (
                    current_app.static_folder,
                    self.source_folder,
                    path.strip('/')
                )
        else:
            item_path = '%s/%s' % (
                    current_app.static_folder,
                    path.strip('/')
                )

        if os.path.isfile(item_path):
            try:
                return Image.open(item_path)
            except IOError as err:
                LOGGER.warning('File not found on path "%s" with error: %s' % (item_path, str(err)))
                return False
        else:
            return False

    def create_cached_item(self, path, content):
        """
        Create cached resource item
        :param path: str
        :param content: Image
        :return: str
        """
        if isinstance(content, Image.Image):
            item_path = '%s/%s/%s' % (
                current_app.static_folder,
                self.cache_folder,
                path.strip('/')
            )
            self.make_dirs(item_path)

            content.save(item_path)

            if os.path.isfile(item_path):
                return '%s/%s/%s' % (current_app.static_url_path, self.cache_folder, path.strip('/'))
            else:  # pragma: no cover
                LOGGER.warning('File is not created on path: %s' % item_path)
                return False
        else:
            return False

    def get_cached_item(self, path):
        """
        Get cached resource item
        :param path: str
        :return: PIL.Image
        """
        item_path = '%s/%s/%s' % (
                current_app.static_folder,
                self.cache_folder,
                path.strip('/')
            )

        if os.path.isfile(item_path):
            try:
                return Image.open(item_path)
            except IOError as err:  # pragma: no cover
                LOGGER.warning('Cached file not found on path "%s" with error: %s' % (item_path, str(err)))
                return False
        else:
            return False

    def check_cached_item(self, path):
        """
        Check for cached resource item exists
        :param path: str
        :return: bool
        """
        item_path = '%s/%s/%s' % (
                current_app.static_folder,
                self.cache_folder,
                path.strip('/')
            )

        if os.path.isfile(item_path):
            return '%s/%s/%s' % (current_app.static_url_path, self.cache_folder, path.strip('/'))
        else:
            return False

    def remove_cached_item(self, path):
        """
        Remove cached resource item
        :param path: str
        :return: bool
        """
        item_path = '%s/%s/%s' % (
                current_app.static_folder,
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
        except OSError as err:
            if err.errno != errno.EEXIST:
                LOGGER.error('Failed to create directory %s with error: %s' % (path, str(err)))
                raise
