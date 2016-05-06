# -*- coding: utf-8 -*-
# (C) Copyright Digital Catapult Limited 2016

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


VERSION = "0.0.3"

setup(name="file_translate",
      version=VERSION,
      description=("Utility to translate the contents of a file by "
                   "running a set of regular expressions over it."),
      author="Digicat",
      packages=["file_translate"],
      package_data={'file_translate': ['config.json']},
      entry_points="""\
      [console_scripts]
      file_translate = file_translate.translate:main
      """)
