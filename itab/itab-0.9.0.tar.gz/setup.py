from distutils.core import setup
from setuptools import find_packages

__author__ = 'Jordi Deu-Pons'
__author_email__ = 'jordi@jordeu.net'
__version__ = '0.9.0'

setup(
    name="itab",
    version=__version__,
    packages=find_packages(),
    author=__author__,
    author_email=__author_email__,
    description="Python tab files parsing and validating schema tools.",
    license="Apache License 2",
    keywords="",
    url="https://github.com/bbglab/itab",
    download_url="https://github.com/bbglab/itab/archive/"+__version__+".tar.gz",
    long_description=__doc__,
    install_requires=['six'],
    entry_points={
        'console_scripts': [
            'itab-check = itab.utils.check:cmdline',
            'itab-help = itab.utils.help:cmdline'
        ]
    }
)
