#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-hipchat',

    version='1.0.3',
    description="Provides easy-to-use integration between Django projects and "
        "the hipchat group chat and IM tool.",

    author="Chris Lamb",
    author_email="chris@chris-lamb.co.uk",
    license="BSD",

    packages=find_packages(),
    include_package_data=True,
    install_requires=(
        'Django>=1.8',
    ),
)
