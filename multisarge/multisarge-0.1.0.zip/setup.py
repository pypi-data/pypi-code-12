# -*- coding: utf-8 -*-

from setuptools import setup


with open('README.rst') as f:
    readme = f.read()

setup(
    name='multisarge',
    version='0.1.0',
    description='Multiprocessing Task Runner Using Sarge',
    long_description=readme,
    author='David A. Salter',
    author_email='david.salter.12@gmail.com',
    url='https://github.com/fireforge/multisarge',
    license='MIT',
    py_modules=['multisarge'],
    install_requires=['sarge'],
)
