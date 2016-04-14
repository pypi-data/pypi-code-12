import os
import shutil
import urllib
import urlparse
from os import makedirs, getcwd
from os.path import basename, join, isdir, exists, split

def generate_unpack_dirname(url_or_path):
    return url_or_path.replace(':', '_').replace('/', '_').replace('.', '_')


def remove(path):
    if exists(path):
        if isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def copy_dir(src, to):
    path, folder_name = split(src)
    target = join(to, folder_name)
    if exists(target):
        shutil.rmtree(target)
    shutil.copytree(src, target)


def download_package(download_dir, package_url, ignore_cache):
    filename = basename(urlparse.urlparse(package_url).path)
    download_path = join(download_dir, filename)

    if not exists(download_dir):
        makedirs(download_dir)

    if exists(download_path) and ignore_cache:
        remove(download_path)

    if not exists(download_path):
        print("Downloading: %s" % package_url)
        urllib.urlretrieve(package_url, filename=download_path)
    return download_path


def get_package_cache_folder_path(cache_dir, url_or_path):
    if not cache_dir:
        cache_dir = get_default_cache_dir()

    download_dir = join(cache_dir, generate_unpack_dirname(url_or_path))
    
    if not exists(download_dir):
        makedirs(download_dir)
    return download_dir


def get_default_cache_dir():
    cache_dir = join(getcwd(), '.coin.cache')
    if not exists(cache_dir):
        makedirs(cache_dir)
    return cache_dir
