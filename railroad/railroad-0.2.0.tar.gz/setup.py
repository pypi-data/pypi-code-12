#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

module_path = os.path.join(os.path.dirname(__file__), 'railroad', '__init__.py')
version_line = [line for line in open(module_path)
                if line.startswith('__version__')][0]
__version__ = eval(version_line.split('__version__ = ')[-1])

readme = open('README.rst').read()
doclink = """
Documentation
-------------

"""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='railroad',
    version=__version__,
    description='A functional library for data processing.',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Jindrich K. Smitka',
    author_email='smitka.j@gmail.com',
    url='https://github.com/s-m-i-t-a/railroad',
    packages=[
        'railroad',
    ],
    package_dir={'railroad': 'railroad'},
    include_package_data=True,
    install_requires=[
        'six>=1.7.3',
        'toolz>=0.7.4',
    ],
    license='MIT',
    zip_safe=False,
    keywords='railroad',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
