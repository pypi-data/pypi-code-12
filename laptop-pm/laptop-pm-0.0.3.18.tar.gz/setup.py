import codecs
import os
import re

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    # https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


long_description = read("README.rst")


# setup a list to scripts which are run as standalone 
scripts = ["scripts/laptop-pm"]

setup(
    name="laptop-pm",
    version=find_version("laptop_pm", "__version__.py"),
    long_description=long_description,
    description="Python powermanagement script for my linux laptop.",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.4",
        "Topic :: System :: Systems Administration",
    ],
    keywords=["laptop powersave"],
    author="Jens Kasten",
    author_email="jens@kasten-edv.de",
    url="http://bitbucket.org/igraltist/laptop-pm",
    license="GNU GPLv3",
    scripts=scripts,
    package_dir={"laptop_pm": "laptop_pm"},
    packages=["laptop_pm"],
    zip_safe=False
)
