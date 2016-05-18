#!/usr/bin/env python

from setuptools import setup, find_packages

from s3_website import pkginfo

# Hack to get around http://bugs.python.org/issue8876#msg208792 on vm with
# shared directory
# http://stackoverflow.com/questions/7719380/python-setup-py-sdist-error-operation-not-permitted
import os

del os.link

setup(
    name=pkginfo.package,
    version=pkginfo.version,
    author=pkginfo.author,
    author_email=pkginfo.author_email,
    url=pkginfo.url,
    download_url=pkginfo.download_url,
    keywords=pkginfo.keywords,
    license=pkginfo.license,
    description=pkginfo.short_description,
    long_description=pkginfo.long_description,

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],

    packages=find_packages(),
    entry_points={
        'console_scripts': [
            's3_website = s3_website.main:main',
        ]
    },

    test_suite='s3_website.tests',
    install_requires=[
        'six',
        'pyaml',
        's3cmd',
    ],
)
