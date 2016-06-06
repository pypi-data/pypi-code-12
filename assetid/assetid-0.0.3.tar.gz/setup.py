from __future__ import with_statement

from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


def version():
    with open('VERSION') as f:
        return f.read().strip()


setup(
    name                = "assetid",
    version             = version(),
    description         = "An ocean data asset ID parser developed and used by Axiom Data Science",
    long_description    = readme(),
    license             = 'MIT',
    author              = "Kyle Wilcox",
    author_email        = "kyle@axiomdatascience.com",
    url                 = "https://github.com/axiom-data-science/assetid",
    packages            = find_packages(),
    classifiers         = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
    ],
    include_package_data = True,
)
