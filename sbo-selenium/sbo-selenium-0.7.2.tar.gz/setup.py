#!/usr/bin/env python

import codecs
from setuptools import setup, find_packages

install_requires = [
    'Django>=1.5',
    'requests',
    'selenium',
]

with codecs.open('README.rst', 'r', 'utf-8') as f:
    long_description = f.read()


version = '0.7.2'  # Remember to update docs/CHANGELOG.rst when this changes

setup(
    name="sbo-selenium",
    version=version,
    packages=find_packages(),
    zip_safe=False,
    description="Selenium testing framework for Django applications",
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
        'Topic :: Software Development :: Testing',
    ],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Jeremy Bowman',
    author_email='jbowman@safaribooksonline.com',
    url='https://github.com/safarijv/sbo-selenium',
    include_package_data=True,
    install_requires=install_requires,
)
