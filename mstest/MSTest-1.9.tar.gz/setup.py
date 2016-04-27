#!/usr/bin/env python

from setuptools import setup

setup(name='MSTest',
    version='1.9',
    description='mindsensors test',
    author='mindsensors.com',
    author_email='contact@mindsensors.com',
    url='http://www.mindsensors.com/',
    py_modules=['script'],
    #scripts=['PiStorms_install_script', 'PiStorms_upgrade_script'],
    entry_points={'console_scripts': ['PiStorms_install=PiStorms_install_script', 'PiStorm_upgrade=PiStorms_upgrade_script']},
    )