#!/usr/bin/env python
import codecs
import os.path
from setuptools import setup
from versiontag import get_version, cache_git_tag


packages = [
    'ups_tnt',
]

setup_requires = [
    'versiontag>=1.0.3',
]

requires = [
    'Django>=1.8.11',
    'requests>=2.9.1',
    'djangorestframework>=3.3.3',
    'python-dateutil>=2.5.2',
]


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)

def read(fname):
    return codecs.open(fpath(fname), encoding='utf-8').read()

cache_git_tag()

setup(
    name='django-ups-tnt',
    description="Django wrapper around UPS Time In Transit JSON API",
    version='1.0.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    author='David Burke',
    author_email='dburke@thelabnyc.com',
    url='https://gitlab.com/thelabnyc/django-ups-tnt',
    license='ISC',
    packages=packages,
    install_requires=requires,
    setup_requires=setup_requires
)
