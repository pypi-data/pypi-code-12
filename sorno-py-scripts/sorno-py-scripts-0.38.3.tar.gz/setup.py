#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os

dependency_libs = [
    "beautifulsoup4",
    "dropbox",
    "feedparser",
    "google_api_python_client",
    "ipython",
    "lxml",
    # https://github.com/ahupp/python-magic
    "python_magic",
    "python_dateutil",
    "requests",
    "six",
    "tzlocal",
]

script_dir = os.path.dirname(os.path.realpath(__file__))

with open("README.rst", "r") as f:
    readme_text = f.read()

setup(
    name="sorno-py-scripts",
    version="0.38.3",
    description="Herman Tai's python scripts all prefixed with \"sorno_\"",
    long_description=readme_text,
    author="Herman Tai",
    author_email="htaihm@gmail.com",
    license="APLv2",
    url="https://github.com/hermantai/sorno-py-scripts",
    download_url="https://github.com/hermantai/sorno-py-scripts/archive/master.zip",
    packages=[
        "sorno",
    ],
    scripts=[
        os.path.join("scripts", f)
        for f in os.listdir(os.path.join(script_dir, "scripts"))
        if f.endswith(".py")
    ],  # include all py scripts under the scripts directory
    requires=dependency_libs,
    install_requires=dependency_libs,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: Apache Software License",
    ],
)
