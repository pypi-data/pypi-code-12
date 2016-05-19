#!/usr/bin/env python3

import codecs
import os
from setuptools import setup
import re

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('linkbot_firmware_updater/linkbot_firmware_updater.py').read(),
    re.M
    ).group(1)

here = os.path.abspath(os.path.dirname(__file__))
README = codecs.open(os.path.join(here, 'README.md'), encoding='utf8').read()
setup(
    name = "linkbot_firmware_updater",
    packages = ["linkbot_firmware_updater", ],
    version = version,
    entry_points = {
        "console_scripts": ['linkbot-firmware-updater=linkbot_firmware_updater.linkbot_firmware_updater:main']
    },
    install_requires = [
        "PyLinkbot3 >= 3.0.2", 
        "pystk500v2 >= 2.3.0",
        ],
    description = "Firmware Updating Tool for Barobo Linkbots.",
    long_description = README,
    zip_safe = False,
    include_package_data = True,
    author = "David Ko",
    author_email = "david@barobo.com",
    )

