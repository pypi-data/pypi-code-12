# -*- coding: utf-8 -*-

"""setup for CharLCD package"""

import os
from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as file_handler:
        return file_handler.read()

setup(
    name='CharLCD',
    version='0.2.0',
    description='Handler for char lcds (HD44780) @ Raspberry Pi.',
    long_description=(read('readme.md')),
    url='https://kosci@bitbucket.org/kosci/charlcd.git',
    license='MIT',
    author='Bartosz Kościów',
    author_email='kosci1@gmail.com',
    py_modules=['charlcd'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(exclude=['tests*']),
)
