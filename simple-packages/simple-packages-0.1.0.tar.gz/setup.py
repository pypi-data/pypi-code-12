# vim: set et nosi ai ts=4 sts=4 sw=4:
# -*- coding: utf-8 -*-
import os

from setuptools import setup


def read_local_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read().strip()


README = read_local_file('README.md')
VERSION = __import__('simple').__version__
setup(
    name='simple-packages',
    version=VERSION,
    description='Simple, consistent APIs for popular Python packages.',
    long_description=README,
    author='Grok Learning',
    author_email='opensource@groklearning.com',
    maintainer='Grok Learning',
    maintainer_email='opensource@groklearning.com',
    url='https://github.com/groklearning/simple-packages',
    license='MIT',
    package_dir={
        'simple': 'simple',
        'simple.PIL': 'simple/PIL',
    },
    packages=[
        'simple',
        'simple.PIL',
    ],
    install_requires=[
        'pillow >= 3.2.0',
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'python-coveralls',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
