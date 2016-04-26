import codecs
import os
import sys

try:
    from setuptools import setup
except:
    from distutils.core import setup

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

NAME = "bond_zlj"
PACKAGES = ["bond_zlj"]
DESCRIPTION = "this is a package for bond calculation"
LONG_DESCRIPTION = read("README.rst")
KEYWORDS = "finance bond calculation"
AUTHOR = "LinjunZhou"
AUTHOR_EMAIL = "zhoulinjun1994@163.com"
URL = "http://www.baidu.com/"
VERSION = "0.1.1"
LICENSE = "MIT"

setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords = KEYWORDS,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = URL,
    license = LICENSE,
    packages = PACKAGES,
    include_package_data=True,
    zip_safe=True,
)

