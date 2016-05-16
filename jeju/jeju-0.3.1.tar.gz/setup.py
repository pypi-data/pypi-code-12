import os
from setuptools import setup, Extension
from glob import glob

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "jeju",
    version = "0.3.1",
    author = "Choonho Son",
    author_email = "choonho.son@gmail.com",
    description = ("Intelligent provisioning system based on specification documents"),
    license = "BSD",
    keywords = "build configuration markdown",
    url = "https://github.com/pyengine/jeju",
    packages=['jeju','jeju.executor', ],
    long_description=read('README.rst'),
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    zip_safe=True,
    install_requires=['mistune','requests','ruamel.yaml'],
    entry_points = {
        'console_scripts': [
            'jeju = jeju.do:main',
            ],
        },
)

