from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(name='lalalari',
      version=version,
      description="llalari es un proyecto de pruebas",
      long_description="""\
lsjkhasjhaskhakhajkadhsjkashdskjhsdk""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='test',
      author='Alejandro Souto',
      author_email='sorinaso@gmail.com',
      url='http://lalari.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
