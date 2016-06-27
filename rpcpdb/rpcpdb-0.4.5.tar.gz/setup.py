#!/usr/bin/python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="rpcpdb",
    version="0.4.5",
    description="Debug support for RPC servers",
    long_description=open('README.rst').read(),
    author="Ben Bass",
    author_email="benbass@codedstructure.net",
    url="http://bitbucket.org/codedstructure/rpcpdb",
    packages=["rpcpdb"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Debuggers",
    ]
)
