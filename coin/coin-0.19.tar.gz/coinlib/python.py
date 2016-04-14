import os
import shutil
import tarfile
import zipfile
from os import makedirs
from os.path import join, isdir, exists, split

from coinlib.util import remove, get_package_cache_folder_path, download_package, copy_dir


def unpack_python_whl(whl_path, download_dir):

    unpack_root_dir = download_dir

    whl_dir, whl_filename = split(whl_path)
    whl_parts = whl_filename.split('-')
    unpack_dir_name = '%s-%s' % (whl_parts[0], whl_parts[1])
    unpack_dir = join(unpack_root_dir, unpack_dir_name)
    makedirs(unpack_dir)
    with zipfile.ZipFile(whl_path, "r") as z:
        z.extractall(unpack_dir)
    for item in os.listdir(unpack_dir):
        path = join(unpack_dir, item)
        if isdir(path) and item.endswith('.dist-info'):
            remove(path)
    return unpack_dir


def unpack_python_sources(archive_path, download_dir):
    unpack_dir = join(download_dir, 'output')
    path, filename = split(archive_path)
    if filename.endswith('.tar.gz'):
        tarfile.open(archive_path).extractall(unpack_dir)
    else:
        with zipfile.ZipFile(archive_path, "r") as z:
            z.extractall(unpack_dir)
    sub_dirs = os.listdir(unpack_dir)
    if len(sub_dirs) != 1:
        raise Exception('Package %s is expected to contain one folder inside' % archive_path)
    subdir = sub_dirs[0]
    package_dir = join(unpack_dir, subdir)
    for item in os.listdir(package_dir):
        path = join(package_dir, item)
        if isdir(path):
            if item.endswith('.egg-info') or item in ['docs', 'tests', 'test']:
                remove(path)
        else:
            item_name, item_ext = os.path.splitext(item)
            useful_extensions = ['.py', '.pyc', 'pyo', '.pyd', '.dll', '.so']
            if item in ['setup.py', 'test.py', 'tests.py'] or item_ext not in useful_extensions:
                remove(path)
    return package_dir


def get_python_unpack_function(filename):
    unpack_function = None
    if filename.endswith('.whl'):
        unpack_function = unpack_python_whl
    if filename.endswith('.tar.gz') or filename.endswith('.zip'):
        unpack_function = unpack_python_sources
    if unpack_function is None:
        raise Exception('Unknown package type %s' % filename)
    return unpack_function


def install_python_package(cache_folder, url_or_path, ignore_cache, destination):
    package_path = url_or_path
    download_dir = get_package_cache_folder_path(cache_folder, url_or_path)
    if not exists(url_or_path):
        package_path = download_package(download_dir, url_or_path, ignore_cache)
    path, filename = split(package_path)
    unpack = get_python_unpack_function(filename)
    print("Package file: %s" % package_path)

    unpack_dir = unpack(package_path, download_dir)
    print("Unpacked to: %s" % unpack_dir)

    install_to = destination
    copy_dir(unpack_dir, install_to)
    print("Copied to: %s" % install_to)

    shutil.rmtree(unpack_dir, ignore_errors=True)
    print("Cleaned unpack dir: %s" % unpack_dir)
