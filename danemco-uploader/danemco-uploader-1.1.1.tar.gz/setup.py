#!/usr/bin/env python
from setuptools import setup, find_packages
from uploader import __version__

setup(
    name='danemco-uploader',
    version=__version__,
    description="A file and image uploader",
    author="Danemco, LLC",
    author_email='dev@velocitywebworks.com',
    url='https://git.velocitywebworks.com/lib/danemco-uploader',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=1.8',
        'Pillow',
    ],
)
