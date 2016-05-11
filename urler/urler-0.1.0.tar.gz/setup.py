#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# try:
#    import pypandoc
#    long_description = pypandoc.convert('README.md', 'rst')
# except(IOError, ImportError):
#     long_description = open('README.md').read()

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'docopt>=0.6.2',
    'urllib3>=1.9.1',
    'wsgiref>=0.1.2'
]

test_requirements = [
    'mock>=2.0.0'
]

setup(
    name='urler',
    version='0.1.0',
    description="URLer - GET it?",
    long_description=readme + '\n\n' + history,
    author="Joel Bastos",
    author_email='kintoandar@gmail.com',
    url='https://github.com/kintoandar/urler',
    packages=[
        'urler',
    ],
    package_dir={'urler':
                 'urler'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='urler',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
