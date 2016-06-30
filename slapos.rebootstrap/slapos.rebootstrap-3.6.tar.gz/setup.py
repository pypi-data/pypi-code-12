from setuptools import setup, find_packages
version = '3.6'
name = "slapos.rebootstrap"

long_description = open("README.txt").read() + '\n\n'
long_description += open("CHANGES.txt").read()
long_description += """
Technical documentation
=======================
"""
import glob
import os
for f in glob.glob(os.path.join('slapos', 'rebootstrap', '*.txt')):
  long_description += '\n' + open(f).read() + '\n'

setup(
  name=name,
  version=version,
  description="A zc.buildout extension to solve chicken-and-egg problem of"\
      " using python which is built by itself",
  long_description=long_description,
  classifiers=[
      "Development Status :: 4 - Beta",
      "Framework :: Buildout :: Extension",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: Zope Public License",
      "Programming Language :: Python",
      "Topic :: Software Development :: Build Tools",
      "Topic :: Software Development :: Libraries :: Python Modules",
      ],
  entry_points={
     'zc.buildout.extension': ['extension = %s:extension' % name],
     },
  url='https://lab.nexedi.com/nexedi/slapos.rebootstrap',
  maintainer='Kazuhiko Shiozaki',
  maintainer_email='kazuhiko@nexedi.com',
  license='ZPL 2.1',
  include_package_data=True,
  namespace_packages=['slapos'],
  packages=find_packages(),
  zip_safe=True,
  install_requires=[
    'setuptools',
    'zc.buildout >=2.0.0'
    ],
  tests_require=[
      'zope.testing',
    ],
  test_suite='%s.tests.test_suite' % name,
)
