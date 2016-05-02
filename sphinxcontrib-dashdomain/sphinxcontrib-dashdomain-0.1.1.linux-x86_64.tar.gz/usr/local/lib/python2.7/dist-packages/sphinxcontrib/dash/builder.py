# -*- coding: utf-8 -*-
"""
    sphinx.builders.dash
    ~~~~~~~~~~~~~~~~~~~~

    Sphinx Dash builder.

    :copyright: Copyright 2016 by @togakushi
    :license: BSD, see LICENSE for details.
"""

import os
import shutil
import plistlib
import sqlite3
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.util.osutil import ensuredir
from sphinx.errors import ConfigError

Supported_Entry_Types = [
    # https://kapeli.com/docsets#supportedentrytypes
    'Annotation',   'Attribute',  'Binding',      'Builtin',
    'Callback',     'Category',   'Class',        'Command',
    'Component',    'Constant',   'Constructor',  'Define',
    'Delegate',     'Diagram',    'Directive',    'Element',
    'Entry',        'Enum',       'Environment',  'Error',
    'Event',        'Exception',  'Extension',    'Field',
    'File',         'Filter',     'Framework',    'Function',
    'Global',       'Guide',      'Hook',         'Instance',
    'Instruction',  'Interface',  'Keyword',      'Library',
    'Literal',      'Macro',      'Method',       'Mixin',
    'Modifier',     'Module',     'Namespace',    'Notation',
    'Object',       'Operator',   'Option',       'Package',
    'Parameter',    'Plugin',     'Procedure',    'Property',
    'Protocol',     'Provider',   'Provisioner',  'Query',
    'Record',       'Resource',   'Sample',       'Section',
    'Service',      'Setting',    'Shortcut',     'Statement',
    'Struct',       'Style',      'Subroutine',   'Tag',
    'Test',         'Trait',      'Type',         'Union',
    'Value',        'Variable',   'Word',
]

class DashBuilder(StandaloneHTMLBuilder):
    name = 'dash'

    def init(self):
        super(DashBuilder, self).init()

        if self.app.config.dash_name is None:
            self.info('Using project name for `dash_name`')
            self.app.config.dash_name = self.app.config.project
        if self.app.config.dash_name.endswith('.docset'):
            self.app.config.dash_name = os.path.splitext(self.app.config.dash_name)[0]
        if self.app.config.dash_icon_file is None:
            self.info('Using default icon.')
            self.app.config.dash_icon_file = os.path.join(os.path.dirname(__file__), 'icon.png')
        elif not self.app.config.dash_icon_file.endswith('.png'):
            raise ConfigError('Please supply a PNG icon for `dash_icon_file`.')

        self.prepare_docset()


    def prepare_docset(self):
        """
        Create boilerplate files & directories.
        """
        self.outrootdir = self.outdir
        self.docsetdir = os.path.join(self.outrootdir, self.app.config.dash_name + '.docset')
        self.outdir = os.path.join(self.docsetdir, 'Contents/Resources/Documents')

        ensuredir(self.outdir)

        # for sqlite3
        self.sqlite_path = os.path.join(self.docsetdir, 'Contents/Resources/docSet.dsidx')
        if os.path.exists(self.sqlite_path):
            os.remove(self.sqlite_path)
        self.db_conn = sqlite3.connect(self.sqlite_path)
        self.db_conn.execute(
            'CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, '
            'type TEXT, path TEXT)'
        )
        self.db_conn.commit()

        # for plist
        plist_cfg = {
            'CFBundleIdentifier': self.app.config.dash_name,
            'CFBundleName': self.app.config.dash_name,
            'DocSetPlatformFamily': self.app.config.dash_name.lower(),
            'DashDocSetFamily': 'python',
            'isDashDocset': True,
            'dashIndexFilePath': 'index.html',
        }
        plistlib.writePlist(
            plist_cfg,
            os.path.join(self.docsetdir, 'Contents/Info.plist')
        )

        # for icon
        if self.app.config.dash_icon_file:
            shutil.copy2(self.app.config.dash_icon_file, os.path.join(self.docsetdir, 'icon.png'))


    def handle_finish(self):
        with self.db_conn:
            self.info('Writing docset indexes...')
            id = 0
            for domainname, domain in sorted(self.env.domains.items()):
                for name, dispname, type, docname, anchor, prio in sorted(domain.get_objects()):
                    uri = self.get_target_uri(docname)
                    if anchor:
                        uri += '#' + anchor
                    if type.title() in Supported_Entry_Types:
                        id += 1
                        self.db_conn.execute(
                            'INSERT INTO searchIndex VALUES (?, ?, ?, ?)',
                            (id, name, type.title(), uri)
                        )
            self.db_conn.commit()


def setup(app):
    app.add_builder(DashBuilder)
    app.add_config_value('dash_name', None, 'env')
    app.add_config_value('dash_icon_file', None, 'env')
