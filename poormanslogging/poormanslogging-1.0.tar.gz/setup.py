#!/usr/bin/env python

from setuptools import setup

setup(
    name='poormanslogging',
    packages=['poormanslogging'],
    version='1.0',
    description='Dirt simple logging',
    long_description='A simple and straightforward library to log stuff into console. It uses colors and implements a spinner for long-running operations.',
    author='Nicolas Villanueva',
    author_email='villanueva.arg@gmail.com',
    url='https://github.com/nicovillanueva/poormanslogging',
    keywords='logging zeroconfig',
    license='GPLv2+',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
    ],
    install_requires=['colorama']
)
