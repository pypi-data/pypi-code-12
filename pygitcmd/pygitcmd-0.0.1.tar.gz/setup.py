#!/usr/bin/env python
import os
from distutils.core import setup


def read(fname):
    """From an_example_pypi_project (https://pypi.python.org/pypi/an_example_pypi_project). """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="pygitcmd",
    version="0.0.1",
    author="Flowbox",
    author_email="kgadek@flowbox.io",
    maintainer="Konrad Gądek",
    maintainer_email="kgadek@gmail.com",
    description="Thin wrapper around `git` command for Python 3.x",
    long_description=read("README.txt"),
    url="https://bitbucket.org/flowbox-io/pygitcmd",
    license="ISC",
    keywords="git",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: ISC License (ISCL)",
    ],
    packages=["pygitcmd"],
)
