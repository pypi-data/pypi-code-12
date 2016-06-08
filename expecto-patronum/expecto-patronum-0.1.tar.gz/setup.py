# encoding: UTF-8

from setuptools import setup, find_packages

setup(
  name='expecto-patronum',
  version='0.1',
  packages=find_packages(),
  # include_package_data=True,
  install_requires=[
    'Click',
    'PyYAML',
    'pexpect'
  ],
  test_suite = 'tests',
  entry_points='''
  [console_scripts]
  expecto=scripts.cli:expecto
  '''
)
