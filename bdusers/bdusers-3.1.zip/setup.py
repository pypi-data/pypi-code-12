# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bdusers',
    version='3.1',
    description='A bdusers Python project',
    long_description=long_description,
    url='https://github.com/jaritgor',
    author='Users',
    author_email='joseantoniorita@campusciff.net',
    license='MIT',
    classifiers=[],
    keywords=['testing', 'logging', 'example'],
    packages=['bdusers'],
    entry_points={},
)