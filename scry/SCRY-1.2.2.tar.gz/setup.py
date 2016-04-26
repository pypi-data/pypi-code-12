import os
from setuptools import setup

def get_resources():
    rsc = list()
    for d, subdirs, files in os.walk('./resources'):
        rsc += [os.path.join(d[2:],f) for f in files]
    return rsc

setup(
    name         = 'SCRY',
    version      = '1.2.2',
    description  = 'SPARQL Compatible seRvice laYer',
    author       = 'Bas Stringer',
    author_email = 'b.stringer@vu.nl',
    url          = 'http://www.few.vu.nl/',
    license      = 'MIT',
    keywords     = 'scry sparql rdf linked open data service services custom customized extension',
    classifiers  = ['Development Status :: 4 - Beta',
                    'Environment :: Web Environment',
                    'Intended Audience :: Developers',
                    'Intended Audience :: Information Technology',
                    'Intended Audience :: Science/Research',
                    'License :: OSI Approved :: MIT License',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python :: 2',
                    'Programming Language :: Python :: 2.7',
                    'Topic :: Internet :: WWW/HTTP :: WSGI',
                    'Topic :: Scientific/Engineering',
                    'Topic :: Software Development'],

    install_requires     = ['pip>=8.0.0','flask>=0.10.1','rdflib>=4.2.1','sparqlwrapper>=1.7.6'],
    packages             = ['scry','scry.query','scry.services','scry.app'],
    
    entry_points = {'console_scripts'       : ['scry = scry.cmd:cmd'],
                    'rdf.plugins.sparqleval': ['evalService = scry.query.patch:evalService']}
)