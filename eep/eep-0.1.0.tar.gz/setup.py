#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read().splitlines()

install_requires = [x.strip() for x in requirements]

setup(name="eep",
      version="0.1.0",
      description=
      "Emacs style, point based string search-replace library for python",
      long_description=readme,
      author="Abhinav Tushar",
      author_email="abhinav.tushar.vs@gmail.com",
      url="https://github.com/lepisma/eep",
      include_package_data=True,
      install_requires=install_requires,
      license="MIT",
      keywords="eep string search replace",
      packages=find_packages(exclude=["docs", "tests*"]),
      setup_requires=["pytest-runner"],
      tests_require=["pytest"])
