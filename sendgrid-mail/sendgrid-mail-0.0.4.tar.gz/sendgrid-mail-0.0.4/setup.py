#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name='sendgrid-mail',
    version='0.0.4',
    description='Command line utility to send mail via Sendgrid',
    url='https://github.com/diwu1989/sendgrid-mail',
    author='Di Wu',
    author_email='diwu1989@users.noreply.github.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='sendgrid mail sendmail',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['sendgrid>=2.2.1'],
    scripts=['sendgrid-mail']
)
