#! /usr/bin/env python

from setuptools import setup, find_packages
from io import open
import glob, versioneer

setup (
    name = "qlogtask",
    version = versioneer.get_version (),
    description = "Celery task event handlers for qeventlog",
    long_description = open ("README.rst", "r", encoding = "utf-8").read (),
    cmdclass = versioneer.get_cmdclass (),
    classifiers = [
      "Development Status :: 4 - Beta",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: "
      + "GNU General Public License v3 or later (GPLv3+)",
      "Topic :: Utilities",
    ],
    keywords = "celery event logger",
    author = "J C Lawrence",
    author_email = "claw@kanga.nu",
    url = "https://github.com/clearclaw/qlogtask",
    license = "GPL v3",
    packages = find_packages (exclude = ["tests",]),
    package_data = {},
    data_files = [],
    zip_safe = False,
    install_requires = [line.strip ()
                        for line in open ("requirements.txt", "r",
                                          encoding = "utf-8").readlines ()],
    entry_points = {
        "console_scripts": [],
    },
)
