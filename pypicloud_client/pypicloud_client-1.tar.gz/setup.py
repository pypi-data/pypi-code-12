#!/usr/bin/env python

from setuptools import find_packages


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from pip.req import parse_requirements

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = [str(i.req) for i in parse_requirements("requirements.txt", session=False)]
test_requirements = [str(i.req) for i in parse_requirements("test_requirements.txt", session=False)]

VERSION = "1"

setup(
    name="pypicloud_client",
    version=str(VERSION),
    description="Provide a client for pypicloud",
    long_description=readme,
    author="Damien Goldenberg",
    author_email="damdam.gold@gmail.com",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords="pypicloud, client",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
    ],
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com"
)
