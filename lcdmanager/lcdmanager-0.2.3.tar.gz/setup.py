# -*- coding: utf-8 -*-

"""setup for LCDManager package"""

import os
from setuptools import setup, find_packages

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as file_handler:
        return file_handler.read()

setup(
    name='lcdmanager',
    version='0.2.3',
    description='Lcd window manager for char lcds (Hitachi HD44780) @ Raspberry Pi.',
    long_description=(read('readme.md')),
    url='https://bitbucket.org/kosci/lcdmanager.git',
    license='MIT',
    author='Bartosz Kościów',
    author_email='kosci1@gmail.com',
    py_modules=['lcdmanager'],
    include_package_data=True,
    keywords=['charlcd', 'raspberry pi' ,'hd44780' ,'44780', 'hitachi', 'hd 44780', 'lcd', 'char lcd'],
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
        'Topic :: Home Automation',
    ],
    install_requires=[
        'charlcd'
    ],
    packages=find_packages(exclude=['tests*']),
)
