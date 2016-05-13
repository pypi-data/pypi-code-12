# -*- coding: utf-8 -*-
"""
Setup file for the Geometric Shapes Point Cloud package.

@author: Matheus Boni Vicari (matheus.boni.vicari@gmail.com)
"""

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name="geoshapespc",
    version="0.1.1",
    author='Matheus Boni Vicari',
    author_email='matheus.boni.vicari@gmail.com',
    packages=['geoshapespc'],
    url='https://bitbucket.org/matt_bv/geoshapespc',
    license='LICENSE.txt',
    description='Generates a series of 3D point clouds around\
 geometric shapes.',
    long_description=readme(),
    classifiers=['Programming Language :: Python',
                 'Topic :: Scientific/Engineering'],
    keywords='geometric shapes point cloud LiDAR',
    install_requires=[
        "numpy"],
    # ...
)
