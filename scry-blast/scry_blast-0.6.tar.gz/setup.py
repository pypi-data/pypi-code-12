from setuptools import setup

setup(
    name         = 'scry_blast',
    version      = '0.6',
    description  = "A SCRY service to extend SPARQL with procedures that run NCBI's BLAST program",
    author       = 'Bas Stringer',
    author_email = 'b.stringer@vu.nl',
    url          = 'http://www.few.vu.nl/',
    license      = 'MIT',
    keywords     = 'scry sparql math service extension ncbi blast bioinformatics',
    classifiers  = ['Development Status :: 4 - Beta',
                    'Intended Audience :: Developers',
                    'Intended Audience :: Healthcare Industry',
                    'Intended Audience :: Information Technology',
                    'Intended Audience :: Science/Research',
                    'License :: OSI Approved :: MIT License',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python',
                    'Programming Language :: Python :: 2.7',
                    'Topic :: Scientific/Engineering :: Bio-Informatics'],

    install_requires = ['scry>=0.1'],
    packages = ['scry_blast']
)
