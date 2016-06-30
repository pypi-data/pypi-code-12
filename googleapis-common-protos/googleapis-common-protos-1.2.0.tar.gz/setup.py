"""A setup module for the google apis common protos

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import setuptools

from setuptools import setup, find_packages

install_requires = [
  'protobuf>=3.0.0b3'
]

setuptools.setup(
  name='googleapis-common-protos',
  version='1.2.0',

  author='Google Inc',
  author_email='googleapis-packages@google.com',
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: Implementation :: CPython',
  ],
  description='Common protobufs used in Google APIs',
  long_description=open('README.rst').read(),
  install_requires=install_requires,
  license='Apache-2.0',
  packages=find_packages(),
  namespace_packages=['google', 'google.logging', ],
  url='https://github.com/googleapis/googleapis'
)
