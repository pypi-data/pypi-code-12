# -*- coding: UTF-8 -*-
# lvjiyong on 2016/4/20.

from os.path import dirname, join

from setuptools import setup, find_packages

with open(join(dirname(__file__), 'VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()

setup(
    name="pylinux",
    version=version,
    description="pylinux",
    author="lvjiyong",
    author_email='lvjiyong',
    url="https://github.com/lvjiyong/pylinux",
    license="Apache2.0",
    long_description=open('README.md').read(),
    maintainer='lvjiyong',
    platforms=["any"],
    maintainer_email='lvjiyong@gmail.com',
    include_package_data=True,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'fabric',
        'wget',
    ],
)
