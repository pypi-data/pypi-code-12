import os
from setuptools import setup
import glob
# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "ihextools",
    version = "1.1.0",
    author = "Jeff Ciesielski",
    author_email = "jeffciesielski@gmail.com",
    description = ("Simple Intel hex library"),
    license = "MIT",
    keywords = "ihex",
    url = "https://github.com/Jeff-Ciesielski/ihexpy",
    packages=['ihextools'],
    package_dir={'ihextools': 'src/'},
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
