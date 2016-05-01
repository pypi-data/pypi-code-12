#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""

    cd workspace/ocapi/
    hg archive -t tgz /tmp/default.tgz
    cd /tmp
    virtualenv test
    source test/bin/activate
    tar -xvf default.tgz
    cd default/
    python setup.py sdist upload


"""



try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import ocapi.info as pkg


if __name__ == "__main__":
    name = pkg.__name__.split(".")[0]
    setup(
      name=name,
      packages=[name],
      version=pkg.__version__,
      author=pkg.__author__,
      author_email=pkg.__email__,
      long_description=open("README.rst").read(),
      url=pkg.__web__,
      description=pkg.__desc__,
      keywords=[name, 'automatization', 'api', 'furniture', 'optimcabinet', 'vizualization',
                'images', 'calculation', 'optimalization'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'],
      test_suite="test")
