"""
This module implement Google Cloud Storage adapter for Flask-Imagine
"""
import boto
import tempfile
from flask.ext.imagine.adapters.interface import ImagineAdapterInterface
from PIL import Image


class FlaskImagineGoogleCloudAdapter(ImagineAdapterInterface):
    """
    Google Cloud Storage adapter
    """
    gs_conn = None
    bucket = None
    cache_folder = None

    def __init__(self, client_id, client_secret, bucket_name, **kwargs):
        """
        Init adapter
        :param client_id: str
        :param client_secret: str
        :param bucket_name: str
        :param kwargs: dict
        """
        self.gs_conn = boto.connect_gs(client_id, client_secret)
        self.bucket = self.gs_conn.get_bucket(bucket_name)

        self.cache_folder = kwargs.get('cache_folder', 'cache').strip('/')
        self.domain = kwargs.get('domain', '%s.storage.googleapis.com' % bucket_name)
        self.schema = kwargs.get('schema', 'https')

    def get_item(self, path):
        """
        Get resource item
        :param path: str
        :return: PIL.Image
        """
        key = self.bucket.get_key(path)

        if key.exists():
            f = tempfile.NamedTemporaryFile()
            key.get_contents_to_file(f)
            f.seek(0)
            image = Image.open(f.name)
            f.close()

            return image
        else:
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

            key = self.bucket.new_key(item_path)
            key.set_contents_from_file(f)
            key.make_public()

            return self._generate_url_for_key(key)
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

        key = self.bucket.get_key(item_path)

        if key.exists():
            f = tempfile.NamedTemporaryFile()
            key.get_contents_to_file(f)
            f.seek(0)
            image = Image.open(f.name)
            f.close()

            return image
        else:
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

        key = self.bucket.get_key(item_path)

        return self._generate_url_for_key(key) if key and key.exists() else False

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

        key = self.bucket.get_key(item_path)
        if key.exists():
            key.delete()

        return True

    def _generate_url_for_key(self, key):
        """
        :param key: boto.s3.key.Key
        :return: str
        """
        return '%s://%s/%s' % (self.schema, self.domain, key.key)
