import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='aboardly',
    version='0.1.1',
    description='Official Aboardly API library client for python',
    author='Martin',
    author_email='info@aboardly.com',
    license='MIT',
    url="https://github.com/landland/aboardly-python",
    download_url="https://github.com/landland/aboardly-python/tarball/0.1.1",
    install_requires=[
        'requests >= 2.1.0'
    ],
    packages=[
        'aboardly'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
