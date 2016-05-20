# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="burst_statsd",
    version='0.1.5',
    zip_safe=False,
    platforms='any',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    install_requires=['statsd'],
    url="https://github.com/dantezhu/burst_statsd",
    license="MIT",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="upload burst stat to statsd",
)
