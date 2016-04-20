import os
from setuptools import setup, find_packages

__version__ = '0.2.1'

setup(
    name = "cfmeta",
    version = __version__,
    author = "Basil Veerman",
    author_email = "bveerman@uvic.ca",
    license = "GPL-3.0",
    keywords = "climate forecast cf cmor cmip5 cmip3",
    description = ("Utility for processing CF metadata"),
    url = "https://github.com/pacificclimate/cfmeta",
    packages = find_packages('.'),
    extras_require = {
        'netCDF': ['netCDF4'],
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    zip_safe = True,
    )
