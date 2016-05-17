# coding: utf-8
# pylint: disable=W0622
"""cubicweb-saem-ref application packaging information"""

modname = 'saem_ref'
distname = 'cubicweb-saem-ref'

numversion = (0, 11, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = "Référenciel de Système d'Archivage Électronique Mutualisé"
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ =  {'cubicweb': '>= 3.22.2',
                'cubicweb-squareui': None,
                'cubicweb-addressbook': None,
                'cubicweb-compound': '>= 0.2.1',
                'cubicweb-oaipmh': None,
                'cubicweb-relationwidget': '>= 0.3.3',
                'cubicweb-skos': '>= 0.9.0',
                'cubicweb-prov': None,
                'cubicweb-vtimeline': None,
                'cubicweb-signedrequest': None,
                'python-dateutil': None,
                'pytz': None,
                'psycopg2': None,
                'rdflib': '>= 4.1',
               }
__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

from os import listdir as _listdir
from os.path import join, isdir
from glob import glob

THIS_CUBE_DIR = join('share', 'cubicweb', 'cubes', modname)

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')
            and not isdir(join(dirpath, fname))]

data_files = [
    # common files
    [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
    ]
# check for possible extended cube layout
for dname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data',
              'wdoc', 'i18n', 'migration', 'lib', 'dataimport', 'scripts',
              'backports',
              'migration/data'):
    if isdir(dname):
        data_files.append([join(THIS_CUBE_DIR, dname), listdir(dname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package

