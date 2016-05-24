# -*- coding: utf-8 -*-
"""
Setup file for the TIN Filterting package.

@author: Matheus Boni Vicari (matheus.boni.vicari@gmail.com)
"""

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name="tinfiltering",
    version="0.1.4",
    author='Matheus Boni Vicari',
    author_email='matheus.boni.vicari@gmail.com',
    packages=['tinfiltering', 'tinfiltering.tin', 'tinfiltering.test'],
    url='https://bitbucket.org/matt_bv/tinfiltering',
    license='LICENSE.txt',
    description='Filters a set of points in a 2D space.',
    long_description=readme(),
    classifiers=['Programming Language :: Python',
                 'Topic :: Scientific/Engineering'],
    keywords='data filtering TIN delaunay triangulation noise removal',
    data_files=[('tinfiltering/test', ['tinfiltering/test/test_data.npy'])],
    test_suite='nose.collector',
    tests_require=['nose', 'nose-cover3'],
    install_requires=[
        "numpy",
        "scipy"
    ],
    include_package_data=True,
    entry_points={'console_scripts':
                  ['tinfiltering=tinfiltering.command_line:run_cmd']},
    zip_safe=False
)
