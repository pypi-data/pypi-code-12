#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name="python-instagram-ext",
      version="1.3.4",
      description="Life extended Instagram API client",
      license="MIT",
      install_requires=["simplejson","httplib2","six"],
      author="Seraphicer",
      author_email="tomoyuki.kakuda@gmail.com",
      url="http://github.com/Seraphicer/python-instagram",
      packages = find_packages(),
      keywords= "instagram",
      zip_safe = True)
