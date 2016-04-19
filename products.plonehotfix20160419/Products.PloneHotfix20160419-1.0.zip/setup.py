from setuptools import setup, find_packages

import os

long_description = open(
    os.path.join('Products', 'PloneHotfix20160419', "README.txt")).read() + \
    "\n" + \
    open("CHANGES.rst").read()

version = '1.0'

setup(name='Products.PloneHotfix20160419',
      version=version,
      description="Various Plone hotfixes, 2016-04-19",
      long_description=long_description,
      # Get more strings from
      # https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
          ],
      keywords='plone security hotfix patch',
      author='Plone Security Team',
      author_email='security@plone.org',
      url='https://github.com/plone',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      extras_require={
          'test': [
              'Pillow',
              'Plone',
              'Products.PloneTestCase'
              ],
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """
      )
