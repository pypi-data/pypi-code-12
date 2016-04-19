#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

try:
    license = open('LICENSE').read()
except:
    license = None

try:
    readme = open('README.rst').read()
except:
    readme = None

setup(
    name='HiCTornadIO2',
    version='0.1.2',
    author='Serge S. Koval, Taras Drapalyuk',
    author_email='serge.koval@gmail.com, taras@drapalyuk.com',
    packages=['tornadio2'],
    scripts=[],
    url='http://github.com/kulapard/tornadio2/',
    license=license,
    description='Fork of TornadIO2 0.0.4 (by Serge S. Koval). '
                'Socket.io 0.7+ server implementation on top of Tornado framework',
    long_description=readme,
    requires=['simplejson', 'tornado'],
    install_requires=[
        'simplejson>=2.1.0,<3',
        'tornado==4.0.2'
    ]
)
