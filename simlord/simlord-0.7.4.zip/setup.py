# coding: utf-8

import sys

if sys.version_info < (3,4):
    print("At least Python 3.4 is required.", file=sys.stderr)
    exit(1)
try:
    from setuptools import setup
except ImportError:
    print("Please install setuptools before installing this package.", file=sys.stderr)
    exit(1)

# set __version__, __author__, DESCRIPTION
exec(open("simlord/version.py", encoding="utf-8").read())

setup(
    name='simlord',
    version=__version__,
    author=__author__,
    author_email='bianca.stoecker@uni-due.de',
    description=DESCRIPTION,
    long_description = open("README.rst").read(),
    zip_safe=False,
    license='MIT',
    url='https://bitbucket.org/genomeinformatics/simlord/',
    packages=['simlord'],
    entry_points={
        "console_scripts":
            ["simlord = simlord.simlord:main"]
        },
    package_data={'': ['*.css', '*.sh', '*.html']},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
     install_requires=['numpy', 'scipy', 'pysam>=0.8.4', 'dinopy']
)


