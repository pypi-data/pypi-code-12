# Copyright 2016 Alex Orange
# 
# This file is part of LDB Setuptools Coverage.
# 
# LDB Setuptools Coverage is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# LDB Setuptools Coverage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with LDB Setuptools Coverage.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup

setup(name="LDB_Setuptools_Coverage",
      version="0.1",
      description="Package to add coverage command to setuptools",
      author="Alex Orange",
      author_email="alex@eldebe.org",
      packages=['ldb', 'ldb.setuptools'],
      namespace_packages=['ldb', 'ldb.setuptools'],
      url='http://www.eldebe.org/ldb/setuptools/coverage/',
      license='AGPLv3',
      setup_requires=['setuptools_hg'],
      install_requires=['coverage'],
      tests_require=['coverage'],
      test_suite='test',
      classifiers=['Development Status :: 3 - Alpha',
                   'Framework :: Setuptools Plugin',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU Affero General Public License v3',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Software Development :: Testing',
                  ],
      entry_points={
          'distutils.commands': [
              'coverage = ldb.setuptools.coverage:CoverageCommand',
          ],
      },
     )
