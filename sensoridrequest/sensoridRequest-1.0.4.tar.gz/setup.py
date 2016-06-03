"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    short_description = f.read()
setup(
name='sensoridRequest',
# Versions should comply with PEP440.  For a discussion on single-sourcing
# the version across setup.py and the project code, see
# https://packaging.python.org/en/latest/single_source_version.html
version='1.0.4',
description="""Proof of concept packaged installer for carbon black with extended functionality',
long_description='The goal of the project is to provide a way to enable installation of carbon black sensors in a distrubuted manner as well as provide certain extended functionality such as registering users associated with sensors and tracking the sensor ID of systems that are currently being installed.

-Tracking Sensor IDs:
  In order to track the sensor ID of systems Python is being utilized to perform a 
  call to the Carbon Black (CB) Web API & return the sensor ID from the a list of all sensors on the CB server where the computer name of the sensor matches the computer name of the  system being installed.""",
# The project's main PyPi Page.
url='https://pypi.python.org/pypi?%3Aaction=pkg_edit&name=sensoridRequest',
# Author details
author='Gregory Gallaway',
author_email='greg.gallaway@slaitconsulting.com',
# Choose your license
license='MIT',
# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers=[
# How mature is this project? Common values are
#   3 - Alpha
#   4 - Beta
#   5 - Production/Stable
'Development Status ::  3 - Beta - Proof of Concept',
# Indicate who your project is intended for
'Intended Audience :: Developers :: Customer Organization',
'Topic :: Modified Installer :: Carbon Black :: Customer Designated or Designed',
# Pick your license as you wish (should match "license" above)
'License :: OSI Approved :: MIT License',
# Specify the Python versions you support here. In particular, ensure
# that you indicate whether you support Python 2, Python 3 or both.
'Programming Language :: Python :: 2',
'Programming Language :: Python :: 2.6',
'Programming Language :: Python :: 2.7'
    ],
# What does your project relate to?
keywords='Customer Designated, Modified Installer, Carbon Black Installer',
# You can just specify the packages manually here if your project is
# simple. Or you can use find_packages().
packages=find_packages(exclude=['cbapi', 'cbapi-python']),
# Alternatively, if you want to distribute just a my_module.py, uncomment
# this:
py_modules=["sensoridRequest.py"],
# List run-time dependencies here.  These will be installed by pip when
# your project is installed. For an analysis of "install_requires" vs pip's
# requirements files see:
# https://packaging.python.org/en/latest/requirements.html
install_requires=['cbapi', 'simplejson', 'requests','urllib3'],
# List additional groups of dependencies here (e.g. development
# dependencies). You can install these using the following syntax,
# for example:
# $ pip install -e .[dev,test]
extras_require={
    },
# If there are data files included in your packages that need to be
# installed, specify them here.  If using Python 2.6 or less, then these
# have to be included in MANIFEST.in as well.
#package_data={
#'sample': ['package_data.dat'],
#    },
# Although 'package_data' is the preferred approach, in some case you may
# need to place data files outside of your packages. See:
# http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
# In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
#data_files=[('my_data', ['data/data_file'])],
# To provide executable scripts, use entry points in preference to the
# "scripts" keyword. Entry points provide cross-platform support and allow
# pip to create the appropriate form of executable for the target platform.
#entry_points={
#'console_scripts': [
#'sample=sample:main',
#        ],
)
