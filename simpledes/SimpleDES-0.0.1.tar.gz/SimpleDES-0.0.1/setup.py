"""A setuptools based setup module for Dynamic Number"""

from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path, remove, system
from shutil import copyfile

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='SimpleDES',

    version='0.0.1',

    description='A simple Discrete Event Simulator (DES) for G/G/c queueing systems.',
    long_description=long_description,

    package_dir={'SimpleDES': 'src'},

    # The project's main homepage.
    url='https://github.com/opieters/SimpleDES',

    # Author details
    author='Olivier Pieters',
    author_email='me@olivierpieters.be',

    # Choose your license
    license='GPLv3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='discrete event simulator queuing systems analysis',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
)