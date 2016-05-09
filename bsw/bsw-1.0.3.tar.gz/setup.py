"""setup.py: setuptools control.

Borrowed from:
    https://gehrcke.de/2014/02/distributing-a-python-command-line-application/
"""


import re
from setuptools import setup


version = re.search(
    "^__version__\s*=\s*\"(.*)\"",
    open("bsw/__init__.py").read(),
    re.M
).group(1)


with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name = "bsw",
    packages = ["bsw"],
    include_package_data = True,
    entry_points = {
        "console_scripts": ["bsw = bsw.bsw:main"]
    },
    version = version,
    description = "bsw - Build Static Web, a simple static website builder.",
    long_description = long_descr,
    author = "Dave Barker",
    author_email = "david@dbark.co.uk",
    url = "https://github.com/davb5/bsw",
)
