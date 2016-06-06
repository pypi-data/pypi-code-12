# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()


setup(
    name='messenger-sdk',
    version='0.0.2',
    description='Modern Factory Messenger Bot SDK',
    long_description=readme,
    author='Marcin Szepczynski, Grzegorz Waszkowiak',
    author_email='marcin@modernfactory.pl, grzegorz.waszkowiak@modernfactory.pl',
    url='https://github.com/modernfactory/messenger-sdk',
    license='MIT',
    packages=find_packages(exclude=('tests', 'docs'))
)
