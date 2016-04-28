# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('flare/flare.py').read(),
    re.M
    ).group(1)


with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(
    name = "flare",
    packages = ["flare"],
    entry_points = {
        "console_scripts": ['flare = flare.flare:main']
        },
    version = version,
    description = "Data Science Project Builder.",
    long_description = long_descr,
    author = "Francis Bautista",
    author_email = "francis.bautista07@gmail.com",
    url = "http://github.com/francisbautista/flare"
    )
