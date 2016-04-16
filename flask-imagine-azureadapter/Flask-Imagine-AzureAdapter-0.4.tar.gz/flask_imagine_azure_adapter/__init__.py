"""
This module implement Microsoft Azure BLOB storage adapter for Flask-Imagine
"""
import tempfile
import time
from azure.common import AzureMissingResourceHttpError
from azure.storage.blob import BlockBlobService
from flask.ext.imagine.adapters.interface import ImagineAdapterInterface
from PIL import Image


class FlaskImagineAzureAdapter(ImagineAdapterInterface):
    """
    Microsoft Azure BLOB storage adapter
    """
    blob_service = None
    container_name = None
    cache_folder = None

    def __init__(self, account_name, account_key, container_name, **kwargs):
        """
        Init adapter
        :param access_key: str
        :param secret_key: str
        :param bucket_name: str
        """
        self.blob_service = BlockBlobService(account_name, account_key)
        self.container_name = container_name

        self.cache_folder = kwargs.get('cache_folder', 'cache').strip('/')
        self.domain = kwargs.get('domain', '%s.blob.core.windows.net/%s' % (account_name, container_name))
        self.schema = kwargs.get('schema', 'https')

    def get_item(self, path):
        """
        Get resource item
        :param path: string
        :return: Image
        """
        try:
            f = tempfile.NamedTemporaryFile()
            self.blob_service.get_blob_to_path(self.container_name, path, f.name)
            f.seek(0)
            image = Image.open(f.name)
            f.close()

            return image
        except AzureMissingResourceHttpError:
            return False

    def create_cached_item(self, path, content):
        """
        Create cached resource item
        :param path: str
        :param content: PIL.Image
        :return: str
        """
        if isinstance(content, Image.Image):
            f = tempfile.NamedTemporaryFile()
            content.save(f.name, format=content.format)

            item_path = '%s/%s' % (
                self.cache_folder,
                path.strip('/')
            )

            self.blob_service.create_blob_from_path(self.container_name, item_path, f.name)

            return self._generate_url(item_path)
        else:
            return False

    def get_cached_item(self, path):
        """
        Get cached resource item
        :param path: str
        :return: PIL.Image
        """
        item_path = '%s/%s' % (
                self.cache_folder,
                path.strip('/')
            )

        try:
            f = tempfile.NamedTemporaryFile()
            self.blob_service.get_blob_to_path(self.container_name, item_path, f.name)
            f.seek(0)
            image = Image.open(f.name)
            f.close()

            return image
        except AzureMissingResourceHttpError:
            return False

    def check_cached_item(self, path):
        """
        Check for cached resource item exists
        :param path: str
        :return: bool
        """
        item_path = '%s/%s' % (
                self.cache_folder,
                path.strip('/')
            )

        if self.blob_service.exists(self.container_name, item_path):
            return self._generate_url(item_path)
        else:
            return False

    def remove_cached_item(self, path):
        """
        Remove cached resource item
        :param path: str
        :return: PIL.Image
        """
        item_path = '%s/%s' % (
                self.cache_folder,
                path.strip('/')
            )

        self.blob_service.delete_blob(self.container_name, item_path)

        while self.blob_service.exists(self.container_name, item_path):
            time.sleep(0.5)

        return True

    def _generate_url(self, path):
        """
        :param path: str
        :return: str
        """
        return '%s://%s/%s' % (self.schema, self.domain, path.strip('/'))

