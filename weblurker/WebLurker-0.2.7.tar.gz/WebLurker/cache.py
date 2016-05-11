import os
import pickle
import re
import zlib
from datetime import timedelta, datetime
from urllib.parse import urlsplit

from .exception import CacheError


class BaseCache(object):
    """
    Interface for Cache's objects
    """

    def has_expired(self):
        raise NotImplementedError("Cache object has to implement this method")

    def clear(self):
        raise NotImplementedError("Cache object has to implement this method")

    def __setitem__(self, key, value):
        raise NotImplementedError("Cache object has to implement this method")

    def __getitem__(self, item):
        raise NotImplementedError("Cache object has to implement this method")

    def __contains__(self, item):
        raise NotImplementedError("Cache object has to implement this method")


class PickleCache(BaseCache):
    """
    Saves html content in a pickle. Pickle file is compressed to save space. It's use is not recommended.
    """

    def __init__(self, cache_path='weblurker_cache', expiration_days=30, compression=True):
        self.cache_path = cache_path
        self.html_content = dict()
        self.expiration_days = timedelta(days=expiration_days)
        self.creation_timestamp = datetime.utcnow()
        self.compression = compression
        if os.path.isfile(self.cache_path):
            try:
                with open(self.cache_path, 'rb') as cache_file:
                    if compression:
                        pickle_cache = pickle.loads(zlib.decompress(cache_file.read()))
                    else:
                        pickle_cache = pickle.loads(cache_file.read())
                    self.html_content = pickle_cache.html_content
                    self.expiration_days = pickle_cache.expiration_days
                    self.creation_timestamp = pickle_cache.creation_timestamp
            except:
                raise CacheError(
                    "Error when trying to open cache file. Try deleting the cache file: " + str(self.cache_path))


    def has_expired(self):
        """
        Check if cache has expired
        """
        return datetime.utcnow() > self.creation_timestamp + self.expiration_days

    def clear(self):
        """
        Clears cache system
        """
        self.html_content = dict()
        self.creation_timestamp = datetime.utcnow()
        self.save()

    def __setitem__(self, key, value):
        self.html_content[key] = value
        try:
            if self.compression:
                with open(self.cache_path, 'wb') as cache_file:
                    cache_file.write(zlib.compress(pickle.dumps(self)))
            else:
                with open(self.cache_path, 'wb') as cache_file:
                    cache_file.write(pickle.dumps(self))
        except:
            raise CacheError(
                "Error when trying to save cache file. Try deleting the cache file: " + str(self.cache_path))

    def __getitem__(self, item):
        return self.html_content[item]

    def __contains__(self, item):
        return item in self.html_content


class FileCache(BaseCache):
    """
    Uses directories and files to cache content. Due to some systems' restrictions its use is not recommended.
    """

    max_lenght = 250
    indexes_filename = 'indexes'

    def __init__(self, cache_dir='cache', expiration_days=30, compression=True):
        self.cache_dir = cache_dir
        self.indexes = dict()
        self.expiration_days = timedelta(days=expiration_days)
        self.creation_timestamp = datetime.utcnow()
        self.compression = compression
        if os.path.isfile(os.path.join(self.cache_dir, self.indexes_filename)):
            try:
                with open(os.path.join(self.cache_dir, self.indexes_filename), 'rb') as file:
                    if compression:
                        indexes = pickle.loads(zlib.decompress(file.read()))
                    else:
                        indexes = pickle.loads(file.read())
                    self.indexes = indexes.indexes
                    self.expiration_days = indexes.expiration_days
                    self.creation_timestamp = indexes.creation_timestamp
            except:
                raise CacheError(
                    "Error when trying to open an existing cache file. Try deleting the cache directory at " + str(
                        os.path.join(self.cache_dir, self.indexes_filename)))


    def clear(self):
        """
        Clears cache indexes
        """
        self.indexes = dict()
        self.creation_timestamp = datetime.utcnow()
        try:
            if self.compression:
                with open(os.path.join(self.cache_dir, self.indexes_filename), 'wb') as file:
                    file.write(zlib.compress(pickle.dumps(self)))
            else:
                with open(os.path.join(self.cache_dir, self.indexes_filename), 'wb') as file:
                    file.write(pickle.dumps(self))
        except:
            raise CacheError(
                "Error when trying to save the cache to a file. Try deleting the cache directory at " + str(
                    os.path.join(self.cache_dir, self.indexes_filename)))

    def has_expired(self):
        """
        Check if cache has expired
        """
        return datetime.utcnow() > self.creation_timestamp + self.expiration_days

    def url_to_dir(self, url):
        """
        Translates an url to a valid path, following some restrictions by NTFS system format
        """
        components = urlsplit(url)
        path = components.path
        if not path:
            path = '/index.html'
        elif path.endswith('/'):
            path += 'index.html'
        filename = components.netloc + path + components.query
        # replace invalid characters
        filename = re.sub('[^/0-9a-zA-Z\-.,;_ ]', '_', filename)
        # restrict maximum number of characters
        filename = '/'.join(segment[:self.max_lenght] for segment in filename.split('/'))
        return os.path.join(self.cache_dir, filename)

    def __getitem__(self, item):
        try:
            if self.compression:
                with open(self.indexes[item], 'rb') as file:
                    content = pickle.loads(zlib.decompress(file.read()))
            else:
                try:
                    with open(self.indexes[item], 'r') as file:
                        content = file.read()
                except:
                    with open(self.indexes[item], 'rb') as file:
                        content = file.read()
        except:
            raise CacheError(
                "Error when trying to get cached content from it's file. Try deleting the cache directory at " + str(
                    os.path.join(self.cache_dir, self.indexes_filename)))
        return content

    def __setitem__(self, key, value):
        path = self.url_to_dir(key)
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        try:
            if self.compression:
                path = path + ".p"
                with open(path, 'wb') as file:
                    file.write(zlib.compress(pickle.dumps(value)))
            else:
                if type(value) is not bytes:
                    with open(path, 'w') as file:
                        file.write(value)
                else:
                    with open(path, 'wb') as file:
                        file.write(value)
            try:
                if self.compression:
                    with open(os.path.join(self.cache_dir, self.indexes_filename), 'wb') as file:
                        file.write(zlib.compress(pickle.dumps(self)))
                else:
                    with open(os.path.join(self.cache_dir, self.indexes_filename), 'wb') as file:
                        file.write(pickle.dumps(self))
            except:
                raise CacheError(
                    "Error when trying to save the cache to a file. Try deleting the cache directory at " + str(
                        os.path.join(self.cache_dir, self.indexes_filename)))
        except:
            raise CacheError(
                "Error when trying to write cached content to it's file. Try deleting the cache directory at " + str(
                    os.path.join(self.cache_dir, self.indexes_filename)))
        self.indexes[key] = path

    def __contains__(self, item):
        return item in self.indexes
