# coding: utf-8

from setuptools import setup, find_packages

NAME = "vw-gstore-adapter"
VERSION = "1.0.0"


# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "configparser>=3.3",
    "Jinja2>=2.8",
    "MarkupSafe>=0.23",
    "nose>=1.3.7",
    "requests>=2.9.1",
    "python-swiftclient>=3.0.0"
]


setup(
    name=NAME,
    version=VERSION,
    description="Client for the UNM GSToRE REST Geospatial Data Service",
    author_email="maturner01@gmail.com",
    url="https://virtualwatershed.org/docs",
    keywords=["REST", "Hydrology", "Datastore as a Service"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
)
