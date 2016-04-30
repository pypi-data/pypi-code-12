from setuptools import setup

setup(
    name         = 'scry_math',
    version      = '0.5',
    description  = 'A simple SCRY service to extend SPARQL with basic math procedures',
    author       = 'Bas Stringer',
    author_email = 'b.stringer@vu.nl',
    url          = 'http://www.few.vu.nl/',
    license      = 'MIT',
    keywords     = 'scry sparql math service extension',
    classifiers  = ['Development Status :: 4 - Beta',
                    'Intended Audience :: Developers',
                    'Intended Audience :: Information Technology',
                    'Intended Audience :: Science/Research',
                    'License :: OSI Approved :: MIT License',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python :: 2',
                    'Programming Language :: Python :: 2.7',
                    'Topic :: Scientific/Engineering',
                    'Topic :: Scientific/Engineering :: Mathematics'],

    install_requires = ['scipy>=0.15.0','scry>=0.1'],
    packages = ['scry_math']
)