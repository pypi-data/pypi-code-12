import os
from setuptools import setup

def get_resources():
    rsc = list()
    for d, subdirs, files in os.walk('./resources'):
        rsc += [os.path.join(d[2:],f) for f in files]
    return rsc

setup(
    name         = 'SCRY',
    version      = '1.1.4',
    description  = 'SPARQL Compatible seRvice laYer',
    author       = 'Bas Stringer',
    author_email = 'b.stringer@vu.nl',
    url          = 'http://www.few.vu.nl/',
    license      = 'MIT',
    keywords     = 'scry sparql rdf linked open data service services custom customized extension',

    install_requires     = ['pip>=8.0.0','flask>=0.10.1','rdflib>=4.2.1'],
    packages             = ['scry','scry.query','scry.services','scry.app'],
    package_data         = {'scry': get_resources()},
#    include_package_data = True,
    
    entry_points = {'console_scripts': ['scry = scry.cmd:cmd']}
)
