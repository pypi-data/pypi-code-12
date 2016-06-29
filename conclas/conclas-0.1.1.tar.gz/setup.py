import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "conclas",
    version = "0.1.1",
    author = "ConClas",
    author_email = "hello@conclas.com",
    description = ("The ConClas is a client written in Python to use "
                        "the service Conclas."),
    install_requires = ["requests"],
    license = "BSD",
    keywords = "conclas machine learning pyconclas",
    url = "https://github.com/s1mbi0se/conclas/tree/develop/conclas/clients/pyconclas",
    packages=[
        'conclas',
        'conclas.core',
        'conclas.utils',
        'conclas.exceptions',
    ],
    package_dir={'conclas': 'conclas'},
    long_description=read('README.rst'),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Linguistic",
    ],
)