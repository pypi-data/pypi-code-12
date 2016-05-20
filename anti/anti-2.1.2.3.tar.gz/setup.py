#!/usr/bin/env python

from setuptools import setup

bitbucket_url = 'https://gprohorenko@bitbucket.org/gprohorenko/anti'

setup(
    name='anti',
    version='2.1.2.3',
    description='SeoUtils',
    long_description=open('README.rst', 'r').read(),
    author='blinchik',
    author_email='prohorenko_gena_@mail.ru',
    download_url='https://bitbucket.org/gprohorenko/anti/downloads/anti.tar.gz',
    url=bitbucket_url,
    include_package_data=True,
    license='MIT License',
    zip_safe=False,
    packages=['anti'],
    install_requires=[
        "beautifulsoup4>=4.3.2",
        "requests>=2.0.0",
        "Flask-Migrate>=1.2.0",
        "Flask-SQLAlchemy>=2.0",
        "psycopg2>=2.5.4",
        "redis>=2.10.3",
        "python-whois>=0.3.1",
    ],
)
