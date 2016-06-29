from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext
import os

setup(name='chandan',
      version='0.0',
      description='Chandan on the go',
      url='https://github.com/csinva/chandan',
      author='Chandan Singh',
      author_email='csinva@yahoo.com',
      license='MIT',
      packages=['chandan'],
      zip_safe=False)
