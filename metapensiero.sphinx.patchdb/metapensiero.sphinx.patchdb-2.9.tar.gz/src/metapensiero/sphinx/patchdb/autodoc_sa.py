# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Augment DataDocumenter to show SA SQL statements
# :Created:   mar 11 ago 2015 11:44:44 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: Copyright (C) 2015, 2016 Lele Gaifax
#

"Reimplement Sphinx's :py:class:`DataDocumenter` to emit SA query SQL statements."

from __future__ import unicode_literals

from sphinx.ext import autodoc
from sqlalchemy.sql.selectable import Select

try:
    from sqlparse import format as sqlformat
except ImportError:
    def sqlformat(sql, **kw):
        return sql


class DataDocumenter(autodoc.ModuleLevelDocumenter):
    """
    Customized DataDocumenter that knows about SA Select
    """

    objtype = 'data'
    member_order = 40
    priority = -10
    option_spec = dict(autodoc.ModuleLevelDocumenter.option_spec)
    option_spec["annotation"] = autodoc.annotation_option

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return isinstance(parent, autodoc.ModuleDocumenter) and isattr

    def add_directive_header(self, sig):
        autodoc.ModuleLevelDocumenter.add_directive_header(self, sig)
        sourcename = self.get_sourcename()

        if not isinstance(self.object, Select):
            if not self.options.annotation:
                try:
                    objrepr = autodoc.object_description(self.object)
                except ValueError:
                    pass
                else:
                    self.add_line('   :annotation: = ' + objrepr, sourcename)
            elif self.options.annotation is autodoc.SUPPRESS:
                pass
            else:
                self.add_line('   :annotation: %s' % self.options.annotation,
                              sourcename)

    def add_content(self, more_content, no_docstring=False):
        autodoc.ModuleLevelDocumenter.add_content(self, more_content, no_docstring)
        if isinstance(self.object, Select):
            sql = sqlformat(str(self.object), reindent=True)
            self.add_line(".. code-block:: sql", "")
            self.add_line("", "")
            for line in sql.splitlines():
                self.add_line("   " + line, "")

    def document_members(self, all_members=False):
        pass


def setup(app):
    "Setup the Sphinx environment."

    autodoc.add_documenter(DataDocumenter)
