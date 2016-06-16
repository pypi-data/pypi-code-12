""" setup for app """
import re
from setuptools import setup

setup(
    name = "pthapa-first-app",
    packages = ["firstapp"],
    entry_points = {
        "console_scripts": ['firstapp = firstapp.firstapp:main']
        },
    version = '1.20',
    description = "Python command line application bare bones template.",
    author = "Parmeshwor Thapa",
    author_email = "thapa.parmeshwor@gmail.com",
    url = "",
    )