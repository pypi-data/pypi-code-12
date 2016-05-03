import sys
from setuptools import setup, find_packages



# To install the library, open a Terminal shell, then run this
# file by typing:
#
# python setup.py install
#
# You need to have the setuptools module installed.
# Try reading the setuptools documentation:
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["urllib3 >= 1.10", "six >= 1.9", "certifi"]

setup(
    name="dwollaswagger",
    version="1.0.9",
    description="Dwolla API V2 client",
    author="Swagger Contributors, David Stancu",
    author_email="david@dwolla.com",
    url="https://developers.dwolla.com",
    keywords=["Swagger", "Dwolla API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description=open('README.rst').read()
)