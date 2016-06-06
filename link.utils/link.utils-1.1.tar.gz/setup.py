# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys
import os


NAME = 'link.utils'
KEYWORDS = 'link utils'
DESC = 'Link utilities'
URL = 'https://github.com/linkdd/link.utils'
AUTHOR = 'David Delassus'
AUTHOR_EMAIL = 'david.jose.delassus@gmail.com'
LICENSE = 'MIT'
REQUIREMENTS = [
    'b3j0f.conf==0.3.18',
    'six==1.10.0'
]

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Topic :: Utilities',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Intended Audience :: Developers',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: Implementation :: CPython'
]


def get_cwd():
    return os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))


def get_version(default='0.1'):
    sys.path.insert(0, get_cwd())
    from link import utils as mod

    return getattr(mod, '__version__', default)


def get_long_description():
    path = os.path.join(get_cwd(), 'README.rst')
    desc = None

    if os.path.exists(path):
        with open(path) as f:
            desc = f.read()

    return desc


def get_scripts():
    path = os.path.join(get_cwd(), 'scripts')
    scripts = []

    if os.path.exists(path):
        for root, _, files in os.walk(path):
            for f in files:
                scripts.append(os.path.join(root, f))

    return scripts


def get_test_suite():
    return 'link'


setup(
    name=NAME,
    keywords=KEYWORDS,
    version=get_version(),
    url=URL,
    description=DESC,
    long_description=get_long_description(),
    license=LICENSE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=find_packages(),
    scripts=get_scripts(),
    test_suite=get_test_suite(),
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS
)
