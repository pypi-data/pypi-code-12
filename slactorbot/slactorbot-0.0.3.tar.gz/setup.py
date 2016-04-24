"""
Slactorbot - A Python Slack Bot with hot patch!
"""

import os
import re
from setuptools import find_packages, setup


def fread(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_version():
    VERSIONFILE = "slactorbot/_version.py"
    verstrline = fread(VERSIONFILE).strip()
    vsre = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(vsre, verstrline, re.M)
    if mo:
        VERSION = mo.group(1)
    else:
        raise RuntimeError("Unable to find version string in %s." %
                           (VERSIONFILE, ))
    return VERSION

dependencies = ['thespian', 'slackclient', 'pyyaml', 'requests']

setup(
    name='slactorbot',
    version=get_version(),
    url='https://github.com/dataloop/slactorbot',
    download_url="https://github.com/dataloop/slactorbot/tarball/v" + get_version(),
    license="MIT",
    author='Steven Acreman',
    author_email='steven.acreman@dataloop.io',
    description='A Python Slack Bot with hot patch!',
    long_description=fread('README.md'),
    keywords="slack bot",
    packages=find_packages(exclude=['tests']),
    exclude_package_data={'': ['config.yaml']},
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            "slactorbot = slactorbot.bot:start",
        ],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators"
    ])
