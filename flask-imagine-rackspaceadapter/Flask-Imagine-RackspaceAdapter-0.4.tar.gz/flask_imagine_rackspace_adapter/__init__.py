"""
This module implement Rackspace Files adapter for Flask-Imagine
"""
import pyrax
import tempfile
import time
from PIL import Image
from StringIO import StringIO
from pyrax.exceptions import NoSuchObject

from flask.ext.imagine.adapters.interface import ImagineAdapterInterface


class FlaskImagineRackspaceAdapter(ImagineAdapterInterface):
    """
    Rackspace Files storage adapter
    """
    cf_conn = None
    container = None
    cache_folder = None

    def __init__(self, region, user_name, api_key, container_name, **kwargs):
        """
        Init adapter
        :param access_key: str
        :param secret_key: str
        :param bucket_name: str
        """
        pyrax.set_setting("identity_type", "rackspace")
        pyrax.set_default_region(region)
        pyrax.set_credentials(user_name, api_key)

        self.cf_conn = pyrax.cloudfiles
        self.container = self.cf_conn.get_container(container_name)

        self.cache_folder = kwargs.get('cache_folder', 'cache').strip('/')

    def get_item(self, path):
        """
        Get resource item
        :param path: string
        :return: Image
        """
        try:
            cf_object = self.container.get_object(path)
        except NoSuchObject:
            return False

        f = tempfile.NamedTemporaryFile()
        f.write(cf_object.fetch())
        f.seek(0)
        image = Image.open(f.name)
        f.close()

        return image

    def create_cached_item(self, path, content):
        """
        Create cached resource item
        :param path: str
        :param content: PIL.Image
        :return: str
        """
        if isinstance(content, Image.Image):
            output = StringIO()
            content.save(output, format=content.format)

            item_path = '%s/%s' % (
                self.cache_folder,
                path.strip('/')
            )

            self.container.store_object(item_path, output.getvalue())

            return '%s/%s' % (self.container.cdn_ssl_uri, item_path)
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
            cf_object = self.container.get_object(item_path)
        except NoSuchObject:
            return False

        f = tempfile.NamedTemporaryFile()
        f.write(cf_object.fetch())
        f.seek(0)
        image = Image.open(f.name)
        f.close()

        return image

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

        try:
            self.container.get_object(item_path)
            return '%s/%s' % (self.container.cdn_ssl_uri, item_path)
        except NoSuchObject:
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

        self.container.delete_object(item_path)

        try:
            while True:
                self.container.get_object(item_path)
                time.sleep(0.5)
        except NoSuchObject:
            return True
