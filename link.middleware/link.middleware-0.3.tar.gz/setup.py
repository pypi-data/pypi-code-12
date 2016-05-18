# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys
import os


NAME = 'link.middleware'
KEYWORDS = 'link middleware'
DESC = 'Provides utilities to make middlewares connecting to a remote service'
URL = 'https://github.com/linkdd/link.middleware'
AUTHOR = 'David Delassus'
AUTHOR_EMAIL = 'david.jose.delassus@gmail.com'
LICENSE = 'MIT'
REQUIREMENTS = [
    'b3j0f.conf==0.3.13',
    'b3j0f.middleware==0.0.10',
    'requests==2.10.0'
]


def get_cwd():
    return os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))


def get_version(default='0.1'):
    sys.path.insert(0, get_cwd())
    from link import middleware as mod

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
    path = os.path.join(get_cwd(), 'tests')

    return 'tests' if os.path.exists(path) else None


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
    install_requires=REQUIREMENTS
)
