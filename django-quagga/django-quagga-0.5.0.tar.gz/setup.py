#!/usr/bin/env python

from setuptools import setup, find_packages

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name="django-quagga",
    description="Library for Django and Stripe",
    long_description=readme + '\n\n' + history,
    author="Steven Skoczen",
    author_email="steven@agoodcloud.com",
    maintainer="Ben Lopatin",
    maintainer_email="ben@benlopatin.com",
    url="https://github.com/bennylope/django-quagga",
    version="0.5.0",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'stripe>=1.0.0',
    ],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
