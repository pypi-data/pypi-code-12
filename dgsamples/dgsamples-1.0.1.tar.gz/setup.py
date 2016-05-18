#from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='dgsamples',
    version='1.0.1',
    author='Nathan Longbotham',
    author_email='nlongbotham@digitalglobe.com',
    packages=find_packages(),
    description='Sample image chips and vectors that can be used for '\
                'unit testing',
    long_description=open('README.rst').read(),
    include_package_data=True
)
