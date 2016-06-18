"""
sdep
----

sdep is a cli for easily deploying a static website using S3.
"""

# pylint: disable=invalid-name

import ast
import re

from setuptools import setup

# Read the version number in from `sdep/__init__.py`.
with open("sdep/__init__.py", "rb") as init_file:
    file_contents = init_file.read().decode("utf-8")
    version_re = re.compile(r"__version__\s+=\s+(.*)")
    version = str(ast.literal_eval(version_re.search(file_contents).group(1)))

setup(
    name="sdep",
    version=version,
    description="A cli for easily deploying static websites",
    author="Matt McNaughton",
    license="MIT",
    author_email="mattjmcnaughton@gmail.com",
    url="https://github.com/mattjmcnaughton/sdep",
    # Make sure to tag releases appropriately.
    download_url="https://github.com/mattjmcnaughton/sdep/tarball/{0}".format(version),
    keywords=["deployments", "cli"],
    # Dependencies for `sdep`.
    install_requires=[
        "boto3>=1.0.0",
        "click>=6.0",
        "simplejson>=3.0",
    ],
    # Install `sdep` to the user's site-packages directory.
    packages=["sdep"],
    # Tell pip to generate a script called `sdep` which will invoke
    # `sdep.cli:main`.
    entry_points={
        "console_scripts": ["sdep = sdep.cli:main"]
    }
)
