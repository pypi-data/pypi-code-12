# -*- coding: utf-8 -*-
# :Project:   metapensiero.extjs.desktop
# :Created:   mar 11 dic 2012 10:03:12 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2012, 2013, 2014, 2016 Lele Gaifax
#

from io import open
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst'), encoding='utf-8') as f:
    CHANGES = f.read()
with open(os.path.join(here, 'version.txt'), encoding='utf-8') as f:
    VERSION = f.read().strip()

setup(
    name='metapensiero.extjs.desktop',
    version=VERSION,
    description="An ExtJS 4 desktop application packaged with extra goodies",
    long_description=README + u'\n\n' + CHANGES,

    author='Lele Gaifax',
    author_email='lele@metapensiero.it',
    url="https://bitbucket.org/lele/metapensiero.extjs.desktop",

    license="GPLv3+",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved ::"
        " GNU General Public License v3 or later (GPLv3+)",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],

    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['metapensiero', 'metapensiero.extjs'],

    install_requires=[
        'setuptools',
    ],

    extras_require={
        'dev': [
            'metapensiero.tool.bump_version',
            'pyramid',
            'readme',
        ]
    },

    message_extractors={
        'src/metapensiero/extjs/desktop/assets/js': [
            ('**.js', 'javascript', None),
        ],
        'src/metapensiero/extjs/desktop/templates': [
            ('extjs-l10n.mako', 'javascript', None),
        ]
    },

    zip_safe=False,

    entry_points="""\
    [console_scripts]
    minify_js_scripts = metapensiero.extjs.desktop.scripts.minifier:main
    [pyramid.scaffold]
    desktop=metapensiero.extjs.desktop.pyramid:DesktopProjectTemplate
    """,
)
