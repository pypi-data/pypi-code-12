from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext
import os

setup(name='andrew',
      version='0.01',
      description='the portable Andrew',
      url='https://github.com/rueberger/andrew',
      author='Andrew Berger',
      author_email='andbberger@gmail.com',
      license='MIT',
      install_requires=[],
      setup_requires=[],
      packages=['andrew'],
      zip_safe=False)
