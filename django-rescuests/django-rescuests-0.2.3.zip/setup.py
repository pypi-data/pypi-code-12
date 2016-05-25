#!/usr/bin/env python2.5
# -*- coding: UTF-8 -*-

try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass

from setuptools import setup, find_packages

setup(
    name = "django-rescuests",
    version = '0.2.3',
    packages = find_packages(exclude=["tests*"]),
    requires = ['django (>=1.6)', 'django_cron'],
    author = "Dimitri Korsch",
    author_email = "korschdima@gmail.com",
    description = "A framework sending, tracking and retrying REST requests in Django.",
    # long_description = open('README.md').read(),
    license = "LICENSE",
    keywords = "requests, fault tollerant, django, framework",
    url = "https://github.com/BloodyD/django_rescuests",
    include_package_data = True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)

