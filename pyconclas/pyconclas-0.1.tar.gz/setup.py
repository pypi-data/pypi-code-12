import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyconclas",
    version = "0.1",
    author = "Wil Filho",
    author_email = "will@simbioseventures.com",
    description = ("The pyconclas is a client written in Python to use "
                        "the service Conclas."),
    install_requires = ["requests"],
    license = "BSD",
    keywords = "conclas machine learning pyconclas",
    url = "https://github.com/s1mbi0se/conclas/tree/develop/conclas/clients/pyconclas",
    packages=[
        'pyconclas',
        'pyconclas.core',
        'pyconclas.utils',
        'pyconclas.exceptions',
    ],
    package_dir={'pyconclas': 'pyconclas'},
    long_description=read('README.md'),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Linguistic",
    ],
)