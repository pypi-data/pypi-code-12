import errno
import os
import shutil
from urllib.request import urlopen
from sets.core.dataset import Dataset


class Step:
    """
    A cached step for processing datasets. Base class for parsing and altering
    datasets.
    """

    def __call__(self):
        """
        The only interface of this class. Parameters and return value are both
        one or more Dataset objects. The excact numbers should be specified by
        subclasses.
        """
        raise NotImplementedError

    @classmethod
    def cache(cls, name, function, *args, **kwargs):
        """
        Run a function that returns a Dataset object. The result is both cached
        and returned. Additional arguments will be forwarded.
        """
        prefix = os.path.join(cls.folder(), name)
        try:
            return Dataset.load(prefix)
        except FileNotFoundError:
            dataset = function(*args, **kwargs)
            dataset.save(prefix)
            return dataset

    @classmethod
    def download(cls, url, filename=None):
        """
        Download a file and return its filename on the local file system. If
        the file is already there, it won't be downloaded again. The filename
        is relative to the caching directory of the current class. It's derived
        from the url if not provided.
        """
        if not filename:
            _, filename = os.path.split(url)
        filename = os.path.join(cls.folder(), filename)
        if os.path.isfile(filename):
            return filename
        print('Download', filename)
        with urlopen(url) as response, open(filename, 'wb') as file_:
            shutil.copyfileobj(response, file_)
        return filename

    @classmethod
    def folder(cls, prefix='~/.dataset'):
        """
        Path that should be used for caching. Return individual paths for all
        subclasses.
        """
        name = cls.__name__.lower()
        path = os.path.expanduser(os.path.join(prefix, name))
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise e
        return path
