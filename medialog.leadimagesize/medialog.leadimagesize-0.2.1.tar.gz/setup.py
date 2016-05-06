from setuptools import setup, find_packages
import os

version = '0.2.1' 

setup(name='medialog.leadimagesize',
      version=version,
      description="Makes it possible to choose size for lead image.",
      long_description=open("README").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
         "Development Status :: 4 - Beta",
          "Framework :: Plone",
          "Framework :: Plone :: 5.0",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
        ],
      keywords='plone zope leadimagesize',
      author='Grieg Medialog [Espen Moe-Nilssen]',
      author_email='espen@medialog.no',
      url='http://github.com/espenmn/medialog.leadimagesize',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['medialog'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'medialog.controlpanel',
          'plone.api',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
