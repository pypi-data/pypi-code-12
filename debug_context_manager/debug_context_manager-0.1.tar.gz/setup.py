#!/usr/bin/python
# -*- coding:Utf-8 -*-

from setuptools import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()


setup(name='debug_context_manager',
      version='0.1',
      description='super simple context manager to print debug message',
      author='Laurent Peuch',
      long_description=read_md("README.md"),
      author_email='cortex@worlddomination.be',
      url='https://github.com/Psycojoker/debug_context_manager',
      install_requires=[],
      packages=[],
      py_modules=['debug_context_manager'],
      license= 'MIT',
      scripts=[],
      keywords='debug',
     )
