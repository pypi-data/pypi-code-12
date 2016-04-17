"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
import os
import edimensionpkg

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='edimdownloader',
    version=edimensionpkg.__version__,
    description='A downloader for Edimension',
    long_description=long_description,
    url='https://github.com/ongteckwu/edimdownloader',
    author=edimensionpkg.__author__,
    author_email='teckwu_ong@mymail.sutd.edu.sg',
    license=edimensionpkg.__license__,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='sutd edimension',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=["requests",
                      "beautifulsoup4",
                      "docopt",
                      "html5lib"],
    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    entry_points={
        'console_scripts': [
            'edimdownloader = edimensionpkg.__main__:main',
        ],
    },
)
