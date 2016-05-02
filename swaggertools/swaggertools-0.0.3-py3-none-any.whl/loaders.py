import os.path
import urllib.parse
import urllib.request
from . import yaml
from .util import is_url
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from io import TextIOWrapper

__all__ = ['load', 'Document', 'IOLoader', 'FilesystemLoader', 'HTTPLoader']

Document = namedtuple('Document', 'uri, content')


def load(uri, base=None):
    if isinstance(uri, TextIOWrapper):
        loader = IOLoader(uri)
    elif is_url(uri) or uri.startswith('file://'):
        loader = HTTPLoader(uri)
    elif uri.startswith('/'):
        loader = FilesystemLoader(uri)
    elif is_url(base):
        uri = urllib.parse.urljoin(base, uri)
        loader = HTTPLoader(uri)
    elif base:
        dirname = os.path.dirname(base)
        uri = os.path.join(dirname, uri)
        uri = os.path.abspath(uri)
        loader = FilesystemLoader(uri)
    else:
        raise ValueError('Cannot load', uri, base)
    return loader


class BaseLoader(metaclass=ABCMeta):

    def __init__(self, uri):
        self.uri = uri

    @abstractmethod
    def load(self):
        """
        Returns:
            Document
        """
        raise NotImplementedError


class IOLoader(BaseLoader):

    def __init__(self, stream):
        self.stream = stream

    @property
    def uri(self):
        return self.stream.name

    def load(self):
        content = yaml.load(self.stream)
        return Document(self.stream.name, content)


class FilesystemLoader(BaseLoader):

    def load(self):
        with open(self.uri) as file:
            content = yaml.load(file)
        return Document(self.uri, content)


class HTTPLoader(BaseLoader):

    def load(self):
        with urllib.request.urlopen(self.uri) as file:
            content = yaml.load(file)
        return Document(self.uri, content)
