#!/usr/bin/env python
"""
Khooshe
"""

from setuptools import setup, find_packages

INSTALL_REQUIRES = []
TESTS_REQUIRES = []


setup(
    name='Khooshe',
    version=0.2,
    description='Big GeoSptial Data Points Visualization Tool',
    author='Mazi Boustani',
    author_email='maziyar_b4@yahoo.com',
    url='https://github.com/MBoustani/Khooshe',
    download_url=('https://github.com/MBoustani/Khooshe/archive/master.zip'),
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    tests_require=TESTS_REQUIRES,
    extras_require={},
    license='Apache V2',
    keywords='big geoSptial data points visualization opensource',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: PyPy",
    ]
)