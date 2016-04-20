# coding: utf-8
"""
    setup
    ~~~~~
    pyextend package setup

    use $ python setup.py register sdist upload
    to upload to the http://pypi.python.org/pypi

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""
# import sys
import codecs
from setuptools import setup, find_packages
# from setuptools.command.test import test as TestCommand

import pyextend


def read_string(*fnames, **kwargs):
    buf = read_lines(*fnames, **kwargs)

    return ''.join(buf)


def read_lines(*fnames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    buf = []
    for fname in fnames:
        buf.extend(codecs.open(fname, encoding=encoding).readlines())
    return buf


# class PyTest(TestCommand):
#     def finalize_options(self):
#         TestCommand.finalize_options(self)
#         self.test_args = []
#         self.test_suite = True
#
#     def run_tests(self):
#         import pytest
#         errcode = pytest.main(self.test_args)
#         sys.exit(errcode)


setup(
    name='pyextend',
    version=pyextend.__version__,
    # tests_require=['pytest'],
    # install_requires=read_lines('requirements.txt'),
    # install_requires=['pytest>=2.8.7'],
    description='the python extend lib',
    author='Vito',
    author_email='vito2015@live.com',
    url='https://github.com/Vito2015/pyextend.git',
    download_url='https://github.com/Vito2015/pyextend.git',
    license='GNU',
    packages=find_packages(),
    # packages=['pyextend'],
    keywords='python extension package',
    long_description=read_string('README'),
    platforms='any',
    zip_safe=True,
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Software Development :: Libraries',
                 ],

)
