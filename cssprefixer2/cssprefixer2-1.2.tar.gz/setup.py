import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "cssprefixer2",
    version = "1.2",
    author = "Metta Ong",
    author_email = "ongspxm@gmail.com",
    description = 'A tool that rewrites your CSS files, adding vendor-prefixed versions of CSS3 rules.',
    license = "MIT",
    keywords = "css3 prefixer",
    url = "https://github.com/ongspxm/cssprefixer2",
    packages=['cssprefixer'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
		"Intended Audience :: Developers",
    ],
)
