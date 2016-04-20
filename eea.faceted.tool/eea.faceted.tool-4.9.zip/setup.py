""" EEA Faceted Tool Installer
"""
import os
from setuptools import setup, find_packages

name = 'eea.faceted.tool'
path = name.split('.') + ['version.txt']
version = open(os.path.join(*path)).read().strip()

setup(name=name,
      version=version,
      description="EEA Faceted Tool",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='EEA faceted navigation tool zope plone4',
      author='European Environment Agency',
      author_email="webadmin@eea.europa.eu",
      url="https://svn.eionet.europa.eu/projects/"
          "Zope/browser/trunk/eea.faceted.tool",
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'tests']),
      namespace_packages=['eea', 'eea.faceted'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'eea.faceted.vocabularies',
          'plone.app.form',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """
      )
