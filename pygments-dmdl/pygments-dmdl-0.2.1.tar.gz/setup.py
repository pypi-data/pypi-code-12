# -*- coding: utf-8 -*-

"""
 Copyright 2016 cocoatomo

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import os, sys

class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

version='0.2.1'
long_description = '\n'.join([
    open(os.path.join('.', 'README.rst')).read(),
])

classifiers = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.5',
    'Topic :: Documentation',
]

setup(
    name='pygments-dmdl',
    version=version,
    description='DMDL lexer and highlighter for Pygments',
    long_description=long_description,
    classifiers=classifiers,
    keywords=[],
    author='cocoatomo',
    author_email='cocoatomo77 at gmail dot com',
    url='https://github.com/cocoatomo/pygments-dmdl',
    license='Apache License (2.0)',
    namespace_packages=['dmdl'],
    packages=find_packages('.'),
    package_dir={'': '.'},
    # package_data = {'': ['buildout.cfg']},
    include_package_data=True,
    install_requires=[],
    entry_points="""
    [pygments.lexers]
    dmdl = dmdl.lexer:DmdlLexer
    """,
    zip_safe=False,
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
)
