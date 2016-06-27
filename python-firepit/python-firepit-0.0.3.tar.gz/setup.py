#!/usr/bin/env python
import os
import re
import sys

from setuptools import setup, find_packages


version = re.compile(r'VERSION\s*=\s*\((.*?)\)')


def get_package_version():
    """returns package version without importing it"""
    base = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(base, "firepit/__init__.py")) as pkg:
        for line in pkg:
            m = version.match(line.strip())
            if not m:
                continue
            return ".".join(m.groups()[0].split(", "))


def get_requirements(filename):
    return open('requirements/' + filename).read().splitlines()


classes = """
    Development Status :: 1 - Planning
    Intended Audience :: Developers
    License :: OSI Approved :: MIT License
    Topic :: System :: Distributed Computing
    Programming Language :: Python
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.5
    Operating System :: OS Independent
"""
classifiers = [s.strip() for s in classes.split('\n') if s]


install_requires = ['requests', ]
if sys.version_info < (3, 0):
    install_requires.append('futures')


setup(
    name='python-firepit',
    version=get_package_version(),
    description='A Python Google firebase framework to handle REST-calls.',
    long_description=open('README.rst').read(),
    keywords=['firebase', 'messaging', 'android'],
    author='Thomas Wehner',
    author_email='thomas.wehner@tro-lan.de',
    url='https://github.com/twe82/python-firepit',
    license='MIT',
    classifiers=classifiers,
    packages=find_packages(exclude=['tests', 'tests.*'], include=('firepit', )),
    install_requires=install_requires,
    test_suite="tests",
    tests_require=['coverage', ],
)
