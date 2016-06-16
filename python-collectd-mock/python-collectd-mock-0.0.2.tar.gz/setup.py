import os

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

setup(
    name="python-collectd-mock",
    version="0.0.2",
    url="https://github.com/winkidney/python-collectd-mock",
    description="A python mock module for collectd plugin unittest test.",
    author="winkidney",
    author_email="winkidney@gmail.com",
    classifiers=[
        "Topic :: Software Development :: Testing",
    ],
    packages=find_packages(here)
)