import os
from setuptools import setup, find_packages

version = '0.0.13'

long_description = \
    open(os.path.join("docs", "source", "README.rst")).read() + "\n" + \
    open(os.path.join("docs", "source", "HISTORY.rst")).read()

setup(name='xmldirector.dita',
      version=version,
      description="XML-Director DITA conversion",
      long_description=long_description,
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Plone",
          "Framework :: Plone :: 4.3",
          "Framework :: Plone :: 5.0",
          "Framework :: Zope2",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='xml-director DOCX XML C-Rex Plone Python DITA',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://pypi.python.org/pypi/xmldirector.dita',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['xmldirector'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'clint',
          'requests',
          'pytidylib',
          'plac'
      ],
      tests_require=['zope.testing'],
      entry_points="""
      [console_scripts]
      dita2html=xmldirector.dita.converter:main
      dita-install=xmldirector.dita.install:main
      html2dita=xmldirector.dita.html2dita:main
      """,
      )
