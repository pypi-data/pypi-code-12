"""Geckoboard setup
"""
from setuptools import setup

setup(
    name='geckoboard',
    version=open('VERSION').read().strip(),
    packages=['geckoboard'],
    license='Apache License 2.0',
    long_description=open('README.txt').read(),
    author='See Contributors',
    author_email='napalm255@gmail.com',
    url='http://pypi.python.org/pypi/geckoboard/',
    description='Geckoboard API Interface (Unofficial)',
    install_requires=[
        'requests >= 2.9.1',
    ],
    setup_requires=[
        'pytest-runner',
    ],
)
