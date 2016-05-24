#!/usr/bin/env python
from codecs import open

from setuptools import find_packages, setup


with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()


setup(
    name='blanc-seo',
    version='0.2',
    description='Blanc SEO for Django',
    long_description=readme,
    url='https://github.com/blancltd/blancseo',
    maintainer='Blanc Ltd',
    maintainer_email='studio@blanc.ltd.uk',
    platforms=['any'],
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    license='BSD',
)
