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

readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://my_checker.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = []
test_requirements = [
    "wheel>=0.22",
    "bumpversion",
    "flake8",
    "tox",
    "coverage",
    "Sphinx",
    "cryptography",
    "PyYAML"
]

setup(
    name='my_checker',
    version='0.1.0',
    description='Quick math checker',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Michael Reuter',
    author_email='mareuternh@gmail.com',
    url='https://github.com/mareuter/my_checker',
    packages=[
        'my_checker',
    ],
    package_dir={'my_checker': 'my_checker'},
    include_package_data=True,
    install_requires=requirements,
    license='MIT',
    zip_safe=False,
    keywords='my_checker',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    test_suite='tests',
    tests_require=test_requirements

)
