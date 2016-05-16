# -*- coding: utf-8 -*-
"""
Copyright (C) 2015, MuChu Hsu
Contributed by Muchu Hsu (muchu1983@gmail.com)
This file is part of BSD license

<https://opensource.org/licenses/BSD-3-Clause>
"""
from setuptools import setup,find_packages

with open("README.txt") as file:
    long_description = file.read()

setup(
    name = "story_chain",
    version = "0.1.1a1",
    author = "MuChu Hsu",
    author_email = "muchu1983@gmail.com",
    maintainer = "MuChu Hsu",
    maintainer_email = "muchu1983@gmail.com",
    url="https://github.com/muchu1983/story_chain",
    description = "muchu's android story chain app with jsonp web service",
    long_description=long_description,
    download_url="https://pypi.python.org/pypi/story_chain",
    platforms = "python 3.4",
    license = "BSD 3-Clause License",
    packages = find_packages(),
    include_package_data = True,
    install_requires = ["bennu>=0.4.1a1"],
    entry_points = {"console_scripts":["story_chain=story_chain.launcher:entry_point"]},
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: Chinese (Traditional)",
        "Natural Language :: Chinese (Simplified)",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.3",
        "Topic :: Internet :: WWW/HTTP",
        ],
)




