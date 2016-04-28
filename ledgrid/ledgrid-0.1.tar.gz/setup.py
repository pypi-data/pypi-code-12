from __future__ import with_statement

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import ledgrid

ledgrid_classifiers = [
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Topic :: Software Development :: Libraries",
    "Topic :: Utilities",
]

with open("README.rst", "r") as fp:
    ledgrid_long_description = fp.read()

setup(name="ledgrid",
      description = 'An 8x8 grid of virtual LEDs implemented in Pygame.',
      version=ledgrid.__version__,
      author="Zeth",
      author_email="theology@gmail.com",
      py_modules=["ledgrid"],
      long_description=ledgrid_long_description,
      license="BSD",
      classifiers=ledgrid_classifiers,
      url = 'https://github.com/zeth/ledgrid', # use the URL to the github repo
      #download_url = 'https://github.com/zeth/ledgrid/tarball/0.1',
)
