#!/usr/bin/python
from setuptools import setup
import os
README = os.path.join(os.path.dirname(__file__), 'README')

long_description = open(README).read() + '\n\n'

setup(name='cobutils',
      version='0.2.4',
      description='Manipulate cobol files from python',
      author='Ferran Pegueroles Forcadell',
      author_email='ferran@pegueroles.com',
      url='https://pypi.python.org/pypi/cobutils',
      long_description=long_description,
      license='GPL',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
      ],
      packages=['cobutils'],
      scripts=["cobextract.py", "cobcreate.py"],
      )
