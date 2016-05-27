from setuptools import setup, find_packages
import sys, os

version = '0.1.0'

setup(name='py-ha-decorator',
      version=version,
      description="A simple pzookeeper HA decorator",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='cswei99',
      author_email='cswei99@gmail.com',
      url='https://github.com/ng-wei/py-ha-decorator',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "kazoo",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
