#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Based on https://github.com/pypa/sampleproject/blob/master/setup.py."""

from __future__ import unicode_literals
from setuptools import setup, find_packages
# To use a consistent encoding
import codecs


def parse_reqs(req_path='./requirements.txt'):
    """Recursively parse requirements from nested pip files."""
    install_requires = []
    with codecs.open(req_path, 'r') as handle:
        # remove comments and empty lines
        lines = (line.strip() for line in handle
                 if line.strip() and not line.startswith('#'))

        for line in lines:
            # check for nested requirements files
            if line.startswith('-r'):
                # recursively call this function
                install_requires += parse_reqs(req_path=line[3:])

            else:
                # add the line as a new requirement
                install_requires.append(line)

    return install_requires


setup(name='genomicassertions',
      author='Daniel Klevebring',
      author_email='daniel.klevebring@gmail.com',
      url='https://github.com/dakl/genomicassertions',
      description='A package to test common files in genomics (.vcf.gz, .bam)',
      version='0.2.5',
      download_url='https://github.com/dakl/genomicassertions/tarball/v0.2.5',
      packages=find_packages(exclude=('tests*', 'docs', 'examples')),
      keywords=['testing', 'genomics'],
      install_requires=parse_reqs()
      )
