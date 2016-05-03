from __future__ import with_statement

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import greencode

greencode_classifiers = [
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Topic :: Software Development :: Libraries",
    "Topic :: Utilities",
]

with open("README.rst", "r") as fp:
    greencode_long_description = fp.read()

setup(name="greencode",
      description = 'Green Code is a simple visual text representation that aims to be useful in LED grid based applications.',
      version=greencode.__version__,
      author="Zeth",
      author_email="theology@gmail.com",
      py_modules=["greencode"],
      long_description=greencode_long_description,
      license="BSD",
      classifiers=greencode_classifiers,
      url = 'http://ledui.github.io/'
)
