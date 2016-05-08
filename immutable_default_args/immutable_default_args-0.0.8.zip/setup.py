#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
from setuptools import(
    setup,
    find_packages
)


description = str("Very small package to automatically safeguard mutable "
                  "function arguments, preventing them from being modified.")


with io.open('README.rst', 'r', encoding='utf-8') as readme_file:
    readme = readme_file.read()


setup(
    name='immutable_default_args',
    version='0.0.8',
    description=description,
    long_description=readme,
    url='http://timmwagener.com/',
    author="Timm Wagener",
    author_email='wagenertimm@gmail.com',
    packages=find_packages(),
    license='MIT',
    zip_safe=False,
    test_suite='tests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
