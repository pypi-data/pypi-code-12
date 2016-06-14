"""Installation script for Python snake_nupic package."""

import os
import sys

from distutils.core import setup

REPO_DIR = os.path.dirname(os.path.realpath(__file__))


def getVersion():
    """
    Get version from local file.
    """
    with open(os.path.join(REPO_DIR, "VERSION"), "r") as versionFile:
        return versionFile.read().strip()


def parse_file(requirementFile):
    try:
        return [
            line.strip()
            for line in open(requirementFile).readlines()
            if not line.startswith("#")
            ]
    except IOError:
        return []


def findRequirements():
    """
    Read the requirements.txt file and parse into requirements for setup's
    install_requirements option.
    """
    requirementsPath = os.path.join(REPO_DIR, "requirements.txt")
    requirements = parse_file(requirementsPath)

    return requirements


if __name__ == "__main__":
    requirements = findRequirements()
    setup(
        name='snake_nupic',
        packages=['snake_nupic'],
        description='A testcase & game for HTM using nupic platform',
        version=getVersion(),
        install_requires=requirements,
        extras_require={"capnp": ["pycapnp==0.5.5"]},
        author="Hui Gao",
        author_email="asterocean@gmail.com",
        url="https://asterocean.com",
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: POSIX :: Linux",
            "Operating System :: Microsoft :: Windows",
            # It has to be "5 - Production/Stable" or else pypi rejects it!
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "Intended Audience :: Science/Research",
            "Topic :: Scientific/Engineering :: Artificial Intelligence"
        ],
        long_description=(
            "pains and desires are the compelling force which droves livings to act"
            "a testcase called snake game introduced pain & desire"
            "hope it could help the snake adjust its act to get desire fulfilled and least pain"
            "using machine learning NuPIC package")
    )
