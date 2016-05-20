#!/usr/bin/env python

from setuptools import setup, find_packages


with open('README.rst') as file:
    readme = file.read()


setup(
    name='Django-Health-Checks',
    version='0.0.1',
    url='http://github.com/juztin/django-health-checks',
    license='BSD',
    author='Justin Wilson',
    author_email='justin@minty.io',
    description='Adds some common health check endpoints (ping, time, status)',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Django>=1.9'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3 :: Only",
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
