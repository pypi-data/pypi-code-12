#!/usr/bin/env python
from setuptools import setup
import envious

setup(
    name='envious',
    version=envious.__version__,
    description='Easy injection of environment variables from .env files.',
    url='https://github.com/BendingSpoons/envious',
    long_description=open('README.rst').read(),
    author='Matteo Danieli',
    author_email='md@bendingspoons.com',
    keywords=['env', 'environment', 'virtualenv', 'multiple', 'configuration'],
    packages=['envious'],
    license='MIT',
)