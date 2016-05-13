#from distutils.core import setup
from setuptools import setup, find_packages

install_requires = [
    'numpy'
    ]

setup(
    name='tinytools',
    version='1.0.3',
    author='Nathan Longbotham',
    author_email='nlongbotham@digitalglobe.com',
    packages=find_packages(),
    description='Small, high-level tools that fill gaps in current Python '
                'tool sets.',
    long_description=open('README.rst').read(),
    install_requires=install_requires,
    test_suite = 'tinytools.tests'
)
