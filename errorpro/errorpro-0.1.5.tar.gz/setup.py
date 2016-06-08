import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "errorpro",
    version = "0.1.5",
    author = "Lukas Bentkamp",
    author_email = "lukas.bentkamp@mailbox.org",
    description = ("ErrorPro allows to do calculations in IPython with physical quantities, which contain a value, error and unit."),
    license = "BSD",
    keywords = "error uncertainty propagation units physics",
    url = "http://github.com/lukasbk/ErrorPro",
    download_url = 'https://github.com/lukasbk/ErrorPro/tarball/0.1.5',
    packages=['errorpro','errorpro.dimensions','errorpro.parsing'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: BSD License",
    ],
)
