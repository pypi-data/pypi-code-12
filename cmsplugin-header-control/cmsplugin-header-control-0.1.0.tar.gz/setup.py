# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from cmsplugin_header_control import __version__

REQUIREMENTS = []

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Framework :: Django :: 1.8',
    'Framework :: Django :: 1.9',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
]

setup(
    name='cmsplugin-header-control',
    version=__version__,
    description='A simple wrapper plugin for managing HTTP headers for django CMS',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/divio/cmsplugin-header-control',
    packages=find_packages(),
    license='LICENSE.txt',
    platforms=['OS Independent'],
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    include_package_data=True,
    zip_safe=False,
    long_description=open('README.rst').read(),
)

