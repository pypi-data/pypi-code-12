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

from setuptools import setup

setup(
    name='storage_stats',
    version='0.1',
    packages=['storagestats'],
    url='https://github.com/pmay/storage-stats',
    license='Apache v2',
    author='Peter May',
    author_email='Peter.May@bl.uk',
    description='Calculates count and average file size of files recorded by file extension',
    entry_points={
        'console_scripts': [
            'storage_stats = storagestats.__main__:main'
        ]
    },
    install_requires=[
        "progressbar2"
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
