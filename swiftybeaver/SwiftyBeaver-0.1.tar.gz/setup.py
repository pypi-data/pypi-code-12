# -*- coding: utf-8 -*-

# The MIT License (MIT)
# https://opensource.org/licenses/MIT
#
# Copyright © 2016 Sebastian Kreutzberger, Steffen Ryll. Some Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''Setup meta data for the SwiftyBeaver Platform.'''

from setuptools import setup


def readme():
    '''Get contents of package readme file.'''

    with open('README.md') as readme_file:
        return readme_file.read()


setup(
    name='SwiftyBeaver',
    version='0.1',
    description='A Python implementation of the SwiftyBeaver Platform.',
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: System :: Logging'
    ],
    url='https://github.com/SwiftyBeaver/SwiftyBeaver-Python',
    author='Steffen Ryll',
    author_email='steffen.ryll@gmx.de',
    license='MIT',
    packages=['swiftybeaver'],
    install_requires=[
        'pycrypto',
        'requests',
        'requests_futures'
    ],
    zip_safe=True,
    test_suite='nose.collector',
    tests_require=['nose']
)
