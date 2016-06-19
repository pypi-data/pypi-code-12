#!/usr/bin/env python
from setuptools import setup
from pip.req import parse_requirements
install_reqs = parse_requirements('requirements.txt', session=False)
requirements = [str(ir.req) for ir in install_reqs]
setup(
  name             = 'FileGenerator',
  version          = '1.0.0',
  description      = 'Universal file generation toolbox',
  author           = 'Josiah Kerley',
  author_email     = 'josiah@kerley.io',
  url              = 'http://josiahkerley.github.io/projects/2016/06/18/filegen.html',
  install_requires = requirements,
  packages         = [
    'FileGen'
  ],
  entry_points     = {
    "console_scripts": [
      "filegen = FileGen:shell_start"
    ]
  },
)