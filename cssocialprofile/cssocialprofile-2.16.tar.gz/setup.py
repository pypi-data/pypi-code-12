from setuptools import setup, find_packages
import sys, os

version = '2.16'

setup(name='cssocialprofile',
      version=version,
      description="SocialProfile app extension",
      long_description=open("README.rst").read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Josu Azpillaga',
      author_email='jazpillaga@codesyntax.com',
      url='http://www.codesyntax.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'python-social-auth',
          'django-registration-redux',
          'tweepy',
          'pyfacebook'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
