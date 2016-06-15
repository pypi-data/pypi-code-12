# Copyright 2016 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Distutils installer for daemonfixture."""

import sys

from setuptools import setup, find_packages


install_requires = [
    "fixtures >= 0.3.6",
    ]
if sys.version_info[0] < 3:
    install_requires.append("subprocess32")

setup(
    name="daemonfixture",
    version="0.1.0",
    packages=find_packages(),

    install_requires=install_requires,
    extras_require=dict(
        test=[
            "testtools",
        ],
    ),

    author="Free Ekanayaka",
    author_email="<free.ekanayaka@canonical.com>",
    description="Fixture for starting and stopping daemon processes in tests",
    license="AGPL",
    keywords="fixtures subprocess",
    url="http://launchpad.net/daemonfixture",
)
