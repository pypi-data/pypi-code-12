import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="redicrypt",
    version="0.0.1",
    author="Chris Dutra",
    author_email="cdutra@apprenda.com",
    description="Python-based cryptography package for redis.",
    license="MIT",
    keywords="redis data cryptography",
    url="http://github.com/dutronlabs/redicrypt",
    packages=['redicrypt'],
    install_requires=['pycrypto'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)