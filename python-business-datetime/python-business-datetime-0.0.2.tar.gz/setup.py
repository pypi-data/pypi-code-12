# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = '0.0.2'

REQUIREMENTS = []

CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
]

setup(
    name="python-business-datetime",
    version=version,
    description="A simple way to calculate working hours between two dates",
    author="Mark Sanders",
    author_email="sdscdeveloper@gmail.com",
    url="http://github.com/ziplokk/BusinessDatetime",
    packages=find_packages(),
    platforms=['OS Independent'],
    license='LICENSE.txt',
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    include_package_data=True,
    zip_safe=False
)
