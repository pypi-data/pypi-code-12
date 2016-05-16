#!/usr/bin/env python

import setuptools

exec(compile(open("simpletap/version.py").read(), "simpletap/version.py", "exec"))
long_description = open("README.rst").read()

setuptools.setup(
    name='simpletap',
    packages=setuptools.find_packages(),
    version=__version__,
    description='Unittest runner producing Test Anything Protocol (TAP) output',
    long_description=long_description,
    author='Renato Alves',
    maintainer='Renato Alves',
    author_email='alves.rjc@gmail.com',
    license='MIT',
    platforms=["any"],
    url="https://github.com/Unode/simpletap",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
