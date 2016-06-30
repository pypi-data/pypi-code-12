""" Package Setup for randomization """

from setuptools import setup

import skdesign


def readme():
    """ Helper function to open the readme file """
    with open('README.md') as readme_file:
        return readme_file.read()

# Check this against the documentation for setuptools
setup(name='skdesign',
      version='0.1',
      description='Tools for Statistical Study Design',
      long_description=readme(),
      keywords='randomization study design trial',
      url='http://github.com/louden/skdesign',
      author='Christopher Louden',
      author_email='chris@loudenanalytics.com',
      license='BSD',
      packages=['skdesign'],
      install_requires=[],
      test_suite='py.test')
