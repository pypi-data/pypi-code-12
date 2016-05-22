# Copyright 2016 Peter May
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import codecs
import os
import re
from setuptools import setup

# Project version approach from http://python-packaging-user-guide.readthedocs.io/en/latest/single_source_version/
# Version specified in storage_stats.__init__.py
def read(*parts):
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='storage_stats',
    version=find_version('storage_stats', '__init__.py'),
    packages=['storage_stats'],
    package_data={'storage_stats': ['data/*']},
    url='https://github.com/pmay/storage-stats',
    license='Apache Licence 2.0',
    author='Peter May',
    author_email='Peter.May@bl.uk',
    description='Calculates count and average file size of files recorded by file extension',
    entry_points={
        'console_scripts': [
            'storage_stats = storage_stats.__main__:main'
        ]
    },
    install_requires=[
        "progressbar2>=3.6.2",
        "scandir>=1.2"
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ]
)
