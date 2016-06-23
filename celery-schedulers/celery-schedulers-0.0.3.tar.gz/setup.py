#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name='celery-schedulers',
    version='0.0.3',
    author='Brent Tubbs',
    author_email='brent.tubbs@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='http://bits.btubbs.com/celery-schedulers',
    description='Celery scheduler backends for Redis and MongoDB',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
