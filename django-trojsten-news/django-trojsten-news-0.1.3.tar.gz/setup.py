#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-trojsten-news',
    version='0.1.3',
    description="""News for django, used in Trojsten seminary web apps""",
    long_description=readme + '\n\n' + history,
    author='Michal Hozza',
    author_email='mhozza@gmail.com',
    url='https://github.com/trojsten/news',
    packages=[
        'news',
    ],
    include_package_data=True,
    install_requires=[
        "Django>=1.8",
        "django-autoslug",
        "Markdown",
        "django-taggit",
        "django-easy-select2",
    ],
    license="BSD",
    zip_safe=False,
    keywords='news',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
