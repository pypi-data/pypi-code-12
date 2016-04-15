"""
This module implement Amazon AWS S3 adapter for Flask-Imagine
"""
import boto
import tempfile
from flask.ext.imagine.adapters.interface import ImagineAdapterInterface
from PIL import Image


class FlaskImagineS3Adapter(ImagineAdapterInterface):
    """
    Amazon AWS S3 storage adapter
    """
    s3_conn = None
    bucket = None
    cache_folder = None

    def __init__(self, access_key, secret_key, bucket_name, **kwargs):
        """
        Init adapter
        :param access_key: str
        :param secret_key: str
        :param bucket_name: str
        """
        self._connect_s3(access_key, secret_key)
        self._connect_to_bucket(bucket_name)

        self.cache_folder = kwargs.get('cache_folder', 'cache').strip('/')
        self.domain = kwargs.get('domain', '%s.s3.amazonaws.com' % bucket_name)
        self.schema = kwargs.get('schema', 'https')

    def _connect_s3(self, access_key, secret_key):
        self.s3_conn = boto.connect_s3(access_key, secret_key)

    def _connect_to_bucket(self, bucket_name):
        self.bucket = self.s3_conn.get_bucket(bucket_name)

    def get_item(self, path):
        """
        Get resource item
        :param path: string
        :return: Image
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
        :param content: Image.Image
        :return:
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

            return key.generate_url(0)
        else:
            return False

    def get_cached_item(self, path):
        """
        Get cached resource item
        :param path: string
        :return:
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
        :param path: string
        :return:
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
        :param path: string
        :return:
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
        :return:
        """
        return '%s://%s/%s' % (self.schema, self.domain, key.key)
