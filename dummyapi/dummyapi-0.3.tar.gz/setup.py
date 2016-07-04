import os
from setuptools import setup, find_packages

# with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    # README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = "dummyapi",
    version = "0.3",
    packages = find_packages(),
    author = "Yeison Cardona",
    author_email = "yeisoneng@gmail.com",
    maintainer = "Yeison Cardona",
    maintainer_email = "yeisoneng@gmail.com",

    #url = "http://www.pinguino.cc/",
    url = "http://yeisoncardona.com/",
    download_url = "https://bitbucket.org/yeisoneng/python-dummyapi/downloads",


    include_package_data=True,
    license = "BSD License",
    description = "Just dummy APIs for Python from Django Rest Framework.",
    # long_description = README,
    #author = "Yeison Cardona",
    #author_email = "yeisoneng@gmail.com",
    classifiers = [
        "Environment :: Web Environment",
        "Framework :: Django",
    ],
)
