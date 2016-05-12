# -*- coding: utf-8 -*-

import re
from setuptools import setup
from setuptools import find_packages

REQUIRES = [
    'six',
    'click',
    'python-dateutil',
    'radon',
    'tabulate',
    'GitPython',
]

def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version

def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content

setup(
    name='pychurn',
    version=find_version('pychurn/__init__.py'),
    description='Identifying hotspots in python code',
    long_description=read('README.rst'),
    author='Joshua Carp',
    author_email='jm.carp@gmail.com',
    url='https://github.com/jmcarp/pychurn',
    packages=find_packages(exclude=('test*', )),
    package_dir={'pychurn': 'pychurn'},
    include_package_data=True,
    install_requires=REQUIRES,
    license=read('LICENSE'),
    zip_safe=False,
    keywords='pychurn',
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
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'pychurn=pychurn.cli:cli',
        ],
    },
)
