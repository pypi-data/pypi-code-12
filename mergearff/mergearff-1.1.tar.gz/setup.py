#-*-coding:utf-8-*-
import sys
from setuptools import *

setup(
    name="mergearff",
    version="1.1",
    author="Uğur Soğukpınar",
    author_email="sogukpinar.ugur@gmail.com",
    url="https://github.com/ugursogukpinar/mergearff",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "mergearff = scripts.mergearff:main",
        ],
    },
    license="LICENSE.txt",
    description="Merge two arff files",
    long_description=open("README.txt").read(),
    install_requires=list(filter(None, [
        "scipy",
    ])),
)