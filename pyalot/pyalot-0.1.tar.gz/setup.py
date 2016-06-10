#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='pyalot',
    version='0.1',
    description='Send Pushalot notifications from the command line or from Python code',
    long_description=readme(),
    keywords='pushalot push notification windowsphone',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    url='http://github.com/mlesniew/pyalot',
    author='Michał Leśniewski',
    author_email='mlesniew@gmail.com',
    license='GPLv3',
    packages=['pyalot'],
    entry_points = {
        'console_scripts': ['pyalot=pyalot.__main__:main'],
    },
    install_requires=[
        'requests',
    ],
)
