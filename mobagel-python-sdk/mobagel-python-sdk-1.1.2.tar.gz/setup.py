import codecs
import os

try:
    from setuptools import setup
except:
    from distutils.core import setup

this_dir = os.path.dirname(__file__)

readme_filename = os.path.join(this_dir, 'README.md')

requirements_filename = os.path.join(this_dir, 'requirements.txt')

PACKAGE_NAME = 'mobagel-python-sdk'
PACKAGE_VERSION = '1.1.2'
PACKAGE_AUTHOR = 'MoBagel'
PACKAGE_AUTHOR_EMAIL = 'us@mobagel.com'

PACKAGE_URL = "https://github.com/MOBAGEL/mobagel-python-sdk"

PACKAGE_DOWNLOAD_URL = \
    'https://github.com/MOBAGEL/mobagel-python-sdk/tarball/' + PACKAGE_VERSION

PACKAGES = ["pybagel"]
PACKAGE_DATA = {
}

PACKAGE_LICENSE = 'LICENSE.txt'
PACKAGE_DESCRIPTION = "MoBagel SDK for Python."

with open(readme_filename) as f:
    PACKAGE_LONG_DESCRIPTION = f.read()

with open(requirements_filename) as f:
    PACKAGE_INSTALL_REQUIRES = [line[:-1] for line in f]

setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    author=PACKAGE_AUTHOR,
    author_email=PACKAGE_AUTHOR_EMAIL,
    url=PACKAGE_URL,
    download_url=PACKAGE_DOWNLOAD_URL,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    license=PACKAGE_LICENSE,
    description=PACKAGE_DESCRIPTION,
    long_description=PACKAGE_LONG_DESCRIPTION,
    install_requires=PACKAGE_INSTALL_REQUIRES,
)