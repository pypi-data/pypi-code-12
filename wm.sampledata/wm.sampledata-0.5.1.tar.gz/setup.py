from setuptools import find_packages
from setuptools import setup


version = '0.5.1'

long_description = (
    open("README.rst").read() + "\n\n" +
    open("CHANGES.rst").read() + "\n"
    )

setup(name='wm.sampledata',
      version=version,
      description="UI and utility methods to generate sampledata for Plone projects",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        'Framework :: Plone',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        ],
      keywords='plone sampledata generation',
      author='Harald Friessnegger',
      author_email='harald (at) webmeisterei dot com',
      url='https://github.com/collective/wm.sampledata',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['wm'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
