import os
from setuptools import setup

# with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    # README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = "kickapp",
    version = "0.4",
    packages = ["kickapp"],

    scripts = [
        "cmd/djangoapk",
        ],


    author = "Yeison Cardona",
    author_email = "yeisoneng@gmail.com",
    maintainer = "Yeison Cardona",
    maintainer_email = "yeisoneng@gmail.com",

    #url = "http://www.pinguino.cc/",
    url = "http://yeisoncardona.com/",
    download_url = "https://bitbucket.org/yeisoneng/python-kickapp/downloads",


    include_package_data=True,
    license = "BSD License",
    description = "Deploy Django application on android as APK.",
    # long_description = README,
    #author = "Yeison Cardona",
    #author_email = "yeisoneng@gmail.com",
    classifiers = [
        "Environment :: Web Environment",
        "Framework :: Django",
    ],
)
