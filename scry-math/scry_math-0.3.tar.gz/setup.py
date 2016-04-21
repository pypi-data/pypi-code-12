from setuptools import setup

setup(
    name         = 'scry_math',
    version      = '0.3',
    description  = 'A simple SCRY service to extend SPARQL with basic math procedures',
    author       = 'Bas Stringer',
    author_email = 'b.stringer@vu.nl',
    url          = 'http://www.few.vu.nl/',
    license      = 'MIT',
    keywords     = 'scry sparql math service extension',

    install_requires = ['numpy>=1.9.0','scry>=0.1'],
    packages = ['scry_math']
)
