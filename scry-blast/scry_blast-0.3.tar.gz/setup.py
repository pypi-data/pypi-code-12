from setuptools import setup

setup(
    name         = 'scry_blast',
    version      = '0.3',
    description  = "A SCRY service to extend SPARQL with procedures that run NCBI's BLAST program",
    author       = 'Bas Stringer',
    author_email = 'b.stringer@vu.nl',
    url          = 'http://www.few.vu.nl/',
    license      = 'MIT',
    keywords     = 'scry sparql math service extension ncbi blast bioinformatics',

    install_requires = ['scry>=0.1'],
    packages = ['scry_blast']
)
