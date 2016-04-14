from os.path import dirname, join

from coinlib.debian import install_deb_package
from coinlib.python import install_python_package
from coinlib.raw import install_raw_package
import pytest

DIR = dirname(__file__)
cache_dir = join(DIR, 'cache.dir')

@pytest.fixture(scope="function")
def fun_setup(request):
    if exists(cache_dir):
        shutil.rmtree(cache_dir)

def test_install_raw_package_explicit_cache():

    url_or_path = join(DIR, 'data', 'test.tar.gz')
    destination = join(DIR, 'install')

    install_raw_package(cache_dir, url_or_path, True, destination, 'test-raw')


def test_install_raw_package_default_cache():

    url_or_path = join(DIR, 'data', 'test.tar.gz')
    destination = join(DIR, 'install')

    install_raw_package(None, url_or_path, True, destination, 'test-raw')

def test_install_python_package_explicit_cache():

    url_or_path = join(DIR, 'data', 'test-1.whl')
    destination = join(DIR, 'install')

    install_python_package(cache_dir, url_or_path, True, destination)

def test_install_python_package_default_cache():

    url_or_path = join(DIR, 'data', 'test-1.whl')
    destination = join(DIR, 'install')

    install_python_package(None, url_or_path, True, destination)


def test_install_debian_package_explicit_cache():

    url_or_path = join(DIR, 'data', 'test.deb')
    destination = join(DIR, 'install')

    install_deb_package(cache_dir, url_or_path, True, destination, 'debtest')


def test_install_debian_package_default_cache():

    url_or_path = join(DIR, 'data', 'test.deb')
    destination = join(DIR, 'install')

    install_deb_package(None, url_or_path, True, destination, 'debtest')
