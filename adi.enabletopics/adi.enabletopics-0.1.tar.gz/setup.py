from setuptools import setup, find_packages
import os

version = '0.1'

long_description = ''
if os.path.exists("README.rst"):
    long_description = open("README.rst").read()

setup(name='adi.enabletopics',
      version=version,
      description="Plone add-on to re-enable old-style-collections 'Topic' disabled by default since of Plone 4.1",
      long_description=long_description,
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Ida Ebkes',
      author_email='contact@ida-ebkes.eu',
      url='https://github.com/ida/adi.enabletopics/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['adi'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
