# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pexpect-serial',
    version='0.0.2',
    description='pexpect with pyserial',
    long_description=readme,
    author='High Wall',
    author_email='hiwall@126.com',
    url='https://github.com/highwall/pexpect-serial',
    license=license,
    package_data={
        '': ['README.md', 'LICENSE']
    },
    packages=find_packages(exclude=('tests', 'docs'))
)

