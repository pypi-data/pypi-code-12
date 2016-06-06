# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

install_requires = [
    'docutils',
]


setup(
    name='django-xray',
    version='0.2.0',
    description='Xray is an developer helper tool for Django.',
    long_description='',
    author='Kindy Lin',
    url='https://github.com/kindy/django-xray',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=install_requires,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ]
)
