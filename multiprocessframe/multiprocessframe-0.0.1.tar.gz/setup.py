import codecs
import os
import sys


try:
    from setuptools import setup
except:
    from distutils.core import setup


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


NAME = "multiprocessframe"
 
PACKAGES = ["multiprocessframe",]

DESCRIPTION = "A multiprocess frame to deal with a series tasks easily."

LONG_DESCRIPTION = read("README.rst")

KEYWORDS = "multiprocess"

AUTHOR = "Shen jiawei"

AUTHOR_EMAIL = "419910650@qq.com"

URL = "http://blog.sjwjiawei.cn/"

VERSION = "0.0.1"

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
        'Operating System :: POSIX :: Linux',
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
