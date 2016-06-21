# coding=utf-8
"""
pytop
-
Active8 (04-03-15)
author: erik@a8.nl
license: GNU-GPL2
"""
from setuptools import setup
setup(name='pytopcmd',
      version='19',
      description='Simpler Unix top command implemented in python',
      url='https://github.com/erikdejonge/pytop',
      author='Erik de Jonge',
      author_email='erik@a8.nl',
      license='GPL',
      entry_points={
          'console_scripts': [
              'pytop=pytopcmd:main',
          ],
      },
      packages=['pytopcmd'],
      zip_safe=True,
      install_requires=['arguments', 'fuzzywuzzy', 'sh', 'readchar', 'dateutils', 'psutil'],
      classifiers=[
          "Programming Language :: Python :: 2",
          "Intended Audience :: Developers",
          "Intended Audience :: System Administrators",
          "Topic :: Utilities",
          "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
          "Operating System :: POSIX",
          "Environment :: MacOS X",
          "Topic :: System",
      ])
