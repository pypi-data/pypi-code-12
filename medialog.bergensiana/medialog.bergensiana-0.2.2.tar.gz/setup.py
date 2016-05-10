import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.2.2'

long_description = (
    read('README.rst') + '\n' 
    )

setup(name='medialog.bergensiana',
      version=version,
      description="An alternative theme for Plone 5.",
      long_description=long_description,
      classifiers=[
          "Environment :: Web Environment",
          "Development Status :: 4 - Beta",
          "Framework :: Plone :: 5.0",
          "Framework :: Zope2",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
        ],
      keywords='web zope plone theme',
      author='Espen Moe-Nilssen',
      author_email='espen@medialog.no',
      url='http://github.com/espenmn/medialog.bergensiana',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['medialog'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.theming',
          'medialog.iconpicker',
          'collective.themefragments',
          'plone.app.themingplugins',
		  'plone.api',
		  'webcouturier.dropdownmenu',
		  'plone.app.contentlisting',
		  'plone.app.mosaic',
		  'z3c.jbot',
      ],
      extras_require={
          'test': [
          ]
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
