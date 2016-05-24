# -*- coding: utf-8 -*-
#
#   This file is part of the Murdock project.
#
#   Copyright 2016 Malte Lichtner
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
This module handles SPHINX projects (based on reStructuredText.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import collections
import json
import logging
import os
import string
import subprocess
import traceback

import murdock.report
import murdock.misc


log = logging.getLogger('report.sphinx')


class SphinxError(Exception):
    pass


class Project(murdock.report.Project):
    """A class to create a Sphinx project (based on reStructuredText).
    """

    def __init__(
            self, mode, title, label, outdir, user=None, build_exec=None,
            builder='html', html_theme='default', html_templatedir=''):
        super(Project, self).__init__(
            mode, title, label, outdir, user, build_exec)
        #: builder used (refer to `sphinx-build --help` for a full list)
        self.builder = builder
        #: name of the Sphinx theme
        self.html_theme = html_theme
        #: directory of html themes
        self.html_themedir = os.path.join('%s', 'data', 'html_themes')
        #: directory of additional template files (e.g. `layout.html`)
        self.html_templatedir = html_templatedir

    def create(self):
        super(Project, self).create()
        self._write_conf()
        self._write_makefile()
        return True

    def get_build_link(self):
        targetpath = os.path.join(self.outdir, '_build', 'html', 'index.html')
        linkname = '%s-report.html' % self.label
        return targetpath, linkname

    def _new_document(self, label):
        return Document(outdir=self.outdir, label=label)

    def _write_indexfile(self):
        index = self._new_document('index')
        toc_labels = list(self._get_toc_docs())
        if toc_labels:
            index.add_paragraph('.. toctree::\n')
            index.add_paragraph('   :hidden:\n')
            index.add_newline()
            for label in toc_labels:
                index.add_paragraph('   %s\n' % label)
            index.add_newline()
        index.add_headline(0, self.title)
        index.add_newline()
        index.add_include_directive(self.label)
        index.write()
        return True

    def build(self):
        self._write_indexfile()
        if self.build_exec is None:
            return False
        builddir = os.path.dirname(self.get_build_link()[0])
        logfilepath = os.path.join(self.outdir, 'build.log')
        log.info(
            'Build Sphinx project in `%s`.',
            murdock.misc.fmtpath(builddir, self.outdir))
        cmd = ['%s' % self.build_exec, '-E', '-b', '%s' % self.builder,
               '%s' % self.outdir, '%s' % builddir]
        try:
            with codecs.open(logfilepath, 'w', encoding='utf-8') as f:
                subprocess.call(cmd, stderr=f, stdout=f)
        except OSError as exc:
            log.error(
                'Sphinx project in `%s` can not be build using the executable '
                '`%s`: %s', murdock.misc.fmtpath(builddir, self.outdir),
                self.build_exec, exc)
            return False
        return True

    def _write_conf(self):
        filepath = os.path.join(self.outdir, 'conf.py')
        if self.user:
            cright = 'copyright = \'%s\'\n' % self.user
        else:
            cright = 'html_show_copyright = False'
        conf = SPHINX_CONFIG_FILE.substitute(
            copyright=cright, version=murdock.__version__, title=self.mode,
            html_theme=self.html_theme, html_themedir=self.html_themedir,
            html_templatedir=self.html_templatedir)
        with codecs.open(filepath, 'w', encoding='utf-8') as f:
            f.write(conf)
        return True

    def _write_makefile(self):
        filepath = os.path.join(self.outdir, 'Makefile')
        if self.build_exec is None:
            build_exec = 'sphinx-build'
        else:
            build_exec = self.build_exec
        with codecs.open(filepath, 'w', encoding='utf-8') as f:
            f.write(SPHINX_MAKEFILE % build_exec)
        return True


class Document(murdock.report.Document):

    def __init__(self, outdir, label, ext='.rst', plot_ext='.png'):
        super(Document, self).__init__(
            outdir=outdir, label=label, ext=ext, plot_ext=plot_ext)

    def add_headline(self, level, text):
        level += self.headline_offset
        chars = ['=', '-', '=', '-', '*', '~']
        try:
            char = chars[level]
        except IndexError:
            raise SphinxError(
                'Headline level %d not implemented (must be <%d).' % (
                    level, len(chars)))
        if self._output:
            self.add_newline()
        if level < 2:
            self._output += '%s\n' % (char * len(text))
        self._output += '%s\n%s\n' % (text, char * len(text))
        self.add_newline()
        return True

    def add_include_directive(self, filelabel, ext='.rst'):
        self._output += '.. include:: %s%s\n' % (filelabel, ext)

    def add_figure(
            self, outdir, label, caption=None, legend=None, ext=None,
            scale=None):
        if True in (
                _v == self.fmt_figure(label) for _v in self._subs.values()):
            return self.fmt_figure(label)
        if ext is None:
            ext = self.plot_ext
        opt_args = {}
        opt_args['target'] = os.path.join('_images', '%s%s' % (label, ext))
        if scale is not None:
            opt_args['scale'] = '%d' % (100 * scale)
        filepath = os.path.join(outdir, '%s%s' % (label, ext))
        s = '.. |%s| image:: %s\n' % (label, filepath)
        for key, val in opt_args.items():
            s += '      %s:%s: %s\n' % (' ' * len(label), key, val)
        self.add_newline()
        self.add_paragraph(s)
        return self.fmt_figure(label)

    def fmt_bullet_list(self, struct, indent=''):
        l = ''
        if isinstance(struct, dict):
            for key, val in struct.items():
                if isinstance(val, list) or isinstance(val, dict):
                    l += '%s* `%s:`\n\n' % (indent, key)
                    l += self.fmt_bullet_list(val, indent + '  ')
                    if l and not l.endswith('\n\n'):
                        l += '\n'
                else:
                    l += '%s* `%s:` %s\n' % (indent, key, val)
        elif isinstance(struct, list):
            for item in struct:
                if isinstance(item, list) or isinstance(item, dict):
                    l += '\n'
                    l += self.fmt_bullet_list(item, indent + '  ')
                    l += '\n'
                else:
                    l += '%s* %s\n' % (indent, item)
        if l.endswith('\n\n'):
            return l[:-1]
        return l

    def fmt_figure(self, text):
        return '|%s|' % text

    def fmt_bold(self, text):
        return '**%s**' % text

    def fmt_italic(self, text):
        return '`%s`' % text

    def get_table(self, ttype=None):
        return ReSTTable(ttype=ttype, subs=self._subs)


class ReSTTable(murdock.report.Table):
    """Class representing a ReStructuredText table.
    """

    def __init__(self, ttype=None, subs=None):
        super(ReSTTable, self).__init__(ttype=ttype, subs=subs)
        self.css_classes = {
            None: 'table-bordered', 'default': 'table-bordered', 'slim':
            'table-striped', 'large': 'table-hovered'}

    def create(self):
        self._init_table_structure()
        self._fill_table()
        if self._subs is not None:
            self.data = murdock.report.substitute_fields(self.data, self._subs)
        self._format_data()
        t = ''
        # Add (optional) HTML directive: css class.
        try:
            t += '.. cssclass:: %s\n' % self.css_classes[self.ttype]
        except KeyError:
            pass
        # Add table headers.
        t += '%s\n' % self._get_subhline()
        try:
            t += '%s\n' % ' '.join(self.data)
            t += '%s\n' % self._get_hline()
        except TypeError:
            pass
        t += '%s\n' % ' '.join(
            _shead for _stable in self.data.values() for _shead in _stable)
        t += '%s\n' % self._get_subhline()
        # Add table rows.
        i = 0
        while True:
            try:
                t += '%s\n' % ' '.join(
                    _col[i] for _stable in self.data.values() for _col in
                    _stable.values())
            except IndexError:
                break
            i += 1
        t += '%s\n' % self._get_subhline()
        return t

    def _get_hline(self):
        return ' '.join('-' * (len(_head)) for _head in self.data)

    def _get_subhline(self):
        return ' '.join(
            '=' * len(_shead) for _stable in self.data.values() for _shead
            in _stable)

    def _isnumeric(self, x):
        try:
            float(x.strip('*'))
        except ValueError:
            return False
        return True


SPHINX_CONFIG_FILE = string.Template(r"""
from __future__ import unicode_literals
import os
import sys

try:
    from murdock import __path__ as MDPATH
except ImportError:
    MDPATH = []


# General

$copyright
project = 'Murdock $version $title'
source_suffix = '.rst'
source_encoding = 'utf-8'
master_doc = 'index'
exclude_patterns = ['_build']
pygments_style = 'sphinx'
templates_path = ['$html_templatedir']

# HTML output

try:
    html_theme_path = ['$html_themedir' % MDPATH[0]]
except (IndexError, TypeError):
    html_theme_path = []
html_theme = '$html_theme'
html_theme_options = {}
html_use_index = True
html_copy_sourcelink = True
html_show_sourcelink = True

# Latex output

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '6pt',
    'fontpkg': '',
    'preamble': '\pagenumbering{arabic} \pagestyle{headings}'
    }
latex_documents = [
    ('index', 'index.tex', u'$title', u'Created by Murdock $version', 'howto'),
    ]
latex_show_urls = True
latex_show_pagerefs = True

""")

SPHINX_MAKEFILE = """
# Makefile for the docking/screening result Sphinx project

SPHINXOPTS    =
SPHINXBUILD   = %s
PAPER         =
BUILDDIR      = _build

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: help clean html dirhtml singlehtml pickle json htmlhelp qthelp \
devhelp epub latex latexpdf text man changes linkcheck doctest gettext

help:
\t@echo "Please use \`make <target>' where <target> is one of"
\t@echo "  html       to make standalone HTML files"
\t@echo "  dirhtml    to make HTML files named index.html in directories"
\t@echo "  singlehtml to make a single large HTML file"
\t@echo "  pickle     to make pickle files"
\t@echo "  json       to make JSON files"
\t@echo "  htmlhelp   to make HTML files and a HTML help project"
\t@echo "  qthelp     to make HTML files and a qthelp project"
\t@echo "  devhelp    to make HTML files and a Devhelp project"
\t@echo "  epub       to make an epub"
\t@echo "  latex      to make LaTeX files, you can set PAPER=a4 or\
 PAPER=letter"
\t@echo "  latexpdf   to make LaTeX files and run them through pdflatex"
\t@echo "  text       to make text files"
\t@echo "  man        to make manual pages"
\t@echo "  texinfo    to make Texinfo files"
\t@echo "  info       to make Texinfo files and run them through makeinfo"
\t@echo "  gettext    to make PO message catalogs"
\t@echo "  changes    to make an overview of all changed/added/deprecated\
 items"
\t@echo "  linkcheck  to check all external links for integrity"
\t@echo "  doctest    to run all doctests embedded in the documentation\
 (if enabled)"

clean:
\t-rm -rf $(BUILDDIR)/*

html:
\t$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
\t@echo
\t@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

dirhtml:
\t$(SPHINXBUILD) -b dirhtml $(ALLSPHINXOPTS) $(BUILDDIR)/dirhtml
\t@echo
\t@echo "Build finished. The HTML pages are in $(BUILDDIR)/dirhtml."

singlehtml:
\t$(SPHINXBUILD) -b singlehtml $(ALLSPHINXOPTS) $(BUILDDIR)/singlehtml
\t@echo
\t@echo "Build finished. The HTML page is in $(BUILDDIR)/singlehtml."

pickle:
\t$(SPHINXBUILD) -b pickle $(ALLSPHINXOPTS) $(BUILDDIR)/pickle
\t@echo
\t@echo "Build finished; now you can process the pickle files."

json:
\t$(SPHINXBUILD) -b json $(ALLSPHINXOPTS) $(BUILDDIR)/json
\t@echo
\t@echo "Build finished; now you can process the JSON files."

htmlhelp:
\t$(SPHINXBUILD) -b htmlhelp $(ALLSPHINXOPTS) $(BUILDDIR)/htmlhelp
\t@echo
\t@echo "Build finished; now you can run HTML Help Workshop with the\
 .hhp project file in $(BUILDDIR)/htmlhelp."

qthelp:
\t$(SPHINXBUILD) -b qthelp $(ALLSPHINXOPTS) $(BUILDDIR)/qthelp
\t@echo
\t@echo "Build finished; now you can run "qcollectiongenerator" with the\
 .qhcp project file in $(BUILDDIR)/qthelp, like this:"
\t@echo "# qcollectiongenerator $(BUILDDIR)/qthelp/default.qhcp"
\t@echo "To view the help file:"
\t@echo "# assistant -collectionFile $(BUILDDIR)/qthelp/default.qhc"

devhelp:
\t$(SPHINXBUILD) -b devhelp $(ALLSPHINXOPTS) $(BUILDDIR)/devhelp
\t@echo
\t@echo "Build finished."
\t@echo "To view the help file:"
\t@echo "# mkdir -p $$HOME/.local/share/devhelp/default"
\t@echo "# ln -s $(BUILDDIR)/devhelp $$HOME/.local/share/devhelp/default"
\t@echo "# devhelp"

epub:
\t$(SPHINXBUILD) -b epub $(ALLSPHINXOPTS) $(BUILDDIR)/epub
\t@echo
\t@echo "Build finished. The epub file is in $(BUILDDIR)/epub."

latex:
\t$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex
\t@echo
\t@echo "Build finished; the LaTeX files are in $(BUILDDIR)/latex."
\t@echo "Run \`make' in that directory to run these through (pdf)latex\
 (use \`make latexpdf' here to do that automatically)."

latexpdf:
\t$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex
\t@echo "Running LaTeX files through pdflatex..."
\t$(MAKE) -C $(BUILDDIR)/latex all-pdf
\t@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/latex."

text:
\t$(SPHINXBUILD) -b text $(ALLSPHINXOPTS) $(BUILDDIR)/text
\t@echo
\t@echo "Build finished. The text files are in $(BUILDDIR)/text."

man:
\t$(SPHINXBUILD) -b man $(ALLSPHINXOPTS) $(BUILDDIR)/man
\t@echo
\t@echo "Build finished. The manual pages are in $(BUILDDIR)/man."

texinfo:
\t$(SPHINXBUILD) -b texinfo $(ALLSPHINXOPTS) $(BUILDDIR)/texinfo
\t@echo
\t@echo "Build finished. The Texinfo files are in $(BUILDDIR)/texinfo."
\t@echo "Run \`make' in that directory to run these through makeinfo\
 (use \`make info' here to do that automatically)."

info:
\t$(SPHINXBUILD) -b texinfo $(ALLSPHINXOPTS) $(BUILDDIR)/texinfo
\t@echo "Running Texinfo files through makeinfo..."
\tmake -C $(BUILDDIR)/texinfo info
\t@echo "makeinfo finished; the Info files are in $(BUILDDIR)/texinfo."

gettext:
\t$(SPHINXBUILD) -b gettext $(I18NSPHINXOPTS) $(BUILDDIR)/locale
\t@echo
\t@echo "Build finished. The message catalogs are in $(BUILDDIR)/locale."

changes:
\t$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) $(BUILDDIR)/changes
\t@echo
\t@echo "The overview file is in $(BUILDDIR)/changes."

linkcheck:
\t$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck
\t@echo
\t@echo "Link check complete; look for any errors in the above output\
 or in $(BUILDDIR)/linkcheck/output.txt."

doctest:
\t$(SPHINXBUILD) -b doctest $(ALLSPHINXOPTS) $(BUILDDIR)/doctest
\t@echo "Testing of doctests in the sources finished, look at the\
 results in $(BUILDDIR)/doctest/output.txt."

"""
