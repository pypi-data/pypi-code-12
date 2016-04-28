import urllib.parse
import os


def http_dirname(url):
    parts = urllib.parse.urlparse(url)
    path = os.path.dirname(parts.path)
    parts = list(parts)
    parts[2] = path
    return urllib.parse.urlunparse(parts)


def http_join(*args):
    url = args[0]
    parts = urllib.parse.urlparse(url)
    path = parts.path
    path = os.path.join(path, *args[1:])
    parts = list(parts)
    parts[2] = path
    return urllib.parse.urlunparse(parts)
