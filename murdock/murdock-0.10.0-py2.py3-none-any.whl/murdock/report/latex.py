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
This module handles Latex projects and documents.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import collections
import logging
import os
import re
import subprocess
import traceback

import murdock.report
import murdock.misc

log = logging.getLogger('report.latex')

SPECIAL_CHARS = {
    r'_': r'\_', r'\\': r'\\\\', r'%': r'\%', r'&': r'\&', r'$': r'\$',
    r'#': r'\#', r'{': r'\{', r'}': r'\}', r'~': r'\~', r'^': r'\^'}


class LatexError(Exception):
    pass


class Project(murdock.report.Project):
    """A class to create a Latex project.
    """

    def __init__(self, mode, title, label, outdir, user=None, build_exec=None):
        super(Project, self).__init__(
            mode=mode, title=title, label=label, outdir=outdir, user=user,
            build_exec=build_exec)

    def get_build_link(self):
        targetpath = os.path.join(self.outdir, '_build', 'index.pdf')
        linkname = '%s-report.pdf' % self.label
        return targetpath, linkname

    def _new_document(self, label):
        return Document(outdir=self.outdir, label=label)

    def _write_indexfile(self):
        toc_labels = self._get_toc_docs().keys()
        index = self._new_document('index')
        header = ''
        header += '\\documentclass[notitlepage]{report}\n'
        header += '\\usepackage{graphicx}\n'
        header += '\\renewcommand{\\familydefault}{\\sfdefault}\n'
        if toc_labels:
            header += '\\makeatletter\n'
            header += '\\newcommand*{\\toccontents}{\\@starttoc{toc}}\n'
            header += '\\makeatother\n'
        if self.user is not None:
            header += '\\author{%s}\n' % self.user
        header += '\\title{%s}\n' % self.title
        header += '\\begin{document}\n'
        content = ''
        content += '\\maketitle\n'
        if toc_labels:
            content += '\\toccontents\n'
        footer = ''
        footer += '\\end{document}\n'
        index.add_paragraph(header)
        index.increase_indent()
        index.add_paragraph(content)
        if toc_labels:
            index.add_headline(0, 'Overview')
        index.add_include_directive(self.label)
        for label in toc_labels:
            index.add_include_directive(label)
        index.decrease_indent()
        index.add_paragraph(footer)
        index.write()
        return True

    def build(self):
        self._write_indexfile()
        if self.build_exec is None:
            return False
        builddir = os.path.abspath(os.path.dirname(self.get_build_link()[0]))
        logfilepath = os.path.join(self.outdir, 'build.log')
        log.info(
            'Build LaTeX project in `%s`.',
            murdock.misc.fmtpath(builddir, self.outdir))
        if not os.path.exists(builddir):
            os.makedirs(builddir)
        filepath = 'index.tex'
        cmd = [
            '%s' % self.build_exec, '-output-directory=%s' % builddir,
            '-interaction=nonstopmode', filepath]
        try:
            with codecs.open(logfilepath, 'w', encoding='utf-8') as f:
                subprocess.call(cmd, stderr=f, stdout=f, cwd=self.outdir)
        except KeyboardInterrupt:
            raise
        except:
            errmsg = traceback.format_exc().splitlines()[-1]
            log.error(
                'LaTeX project in `%s` can not be build using the executable '
                '`%s`: %s', murdock.misc.fmtpath(builddir, self.outdir),
                self.build_exec, errmsg)
            return False
        return True


class Document(murdock.report.Document):

    def __init__(self, outdir, label, ext='.tex', plot_ext='.pdf'):
        super(Document, self).__init__(
            outdir=outdir, label=label, ext=ext, plot_ext=plot_ext)

    def add_figure(
            self, outdir, label, caption=None, legend=None, ext=None,
            scale=None):
        if ext is None:
            ext = self.plot_ext
        kwargs = {}
        if scale is not None:
            kwargs['scale'] = scale
        else:
            kwargs['width'] = r'\textwidth'
        refpath = os.path.join(outdir, '%s%s' % (label, ext))
        return self.fmt_figure(refpath, **kwargs)

    def add_headline(self, level, text):
        level += self.headline_offset
        text = _escape_special_chars(text)
        htypes = [
            'chapter', 'section', 'subsection', 'subsubsection', 'paragraph']
        try:
            htype = htypes[level]
        except IndexError:
            raise LatexError(
                'Headline level %d not implemented (must be <%d).' % (
                    level, len(htypes)))
        self.add_newline()
        self.add_paragraph('\\%s{%s}\n' % (htypes[level], text))
        return True

    def add_include_directive(self, filelabel, ext=''):
        self.add_paragraph('\\include{%s%s}\n' % (filelabel, ext))

    def add_title(self, title):
        self.add_paragraph('\\title{%s}' % title)
        self.add_paragraph('\\maketitle')
        return True

    def add_toc(self, documents):
        self.add_paragraph('\\toccontents')
        return True

    def fmt_bullet_list(self, struct, indent=''):
        l = ''
        if isinstance(struct, dict):
            l += '\\begin{description}\n'
            indent += '  '
            for key, val in struct.iteritems():
                key = _escape_special_chars(key)
                if isinstance(val, list) or isinstance(val, dict):
                    l += '%s\item[%s]\n' % (indent, key)
                    l += self.fmt_bullet_list(val, indent + '  ')
                else:
                    val = _escape_special_chars(val)
                    l += '%s\item[%s] %s\n' % (indent, key, val)
            indent = indent[:-2]
            l += '\\end{description}\n'
        elif isinstance(struct, list):
            l += '%s\\begin{itemize}\n' % indent
            indent += '  '
            for val in struct:
                if isinstance(val, list) or isinstance(val, dict):
                    l += '%s\\item\n' % indent
                    l += self.fmt_bullet_list(val, indent + '  ')
                else:
                    _escape_special_chars(val)
                    l += '%s\\item %s\n' % (indent, val)
            indent = indent[:-2]
            l += '%s\\end{itemize}\n' % indent
        return l

    def fmt_figure(self, text, **kwargs):
        if kwargs:
            opt_str = ', '.join([
                '%s=%s' % (_key, _val) for _key, _val in kwargs.iteritems()])
            return r'\includegraphics[%s]{%s}' % (opt_str, text)
        else:
            return r'\includegraphics{%s}' % text

    def fmt_bold(self, text):
        return r'\textbf{%s}' % text

    def fmt_italic(self, text):
        return r'\textit{%s}' % text

    def get_table(self, ttype=None):
        return LatexTable(ttype=ttype, subs=self._subs)


class LatexTable(murdock.report.Table):
    """Class representing a LatexTable.
    """

    def __init__(self, ttype=None, subs=None):
        super(LatexTable, self).__init__(ttype=ttype, subs=subs)
        self.col_fmts = None
        self.compact = True

    def create(self):
        self._init_table_structure()
        self._fill_table()
        if self.col_fmts is None:
            self._set_column_formatters()
        if not self.compact:
            self._format_data()
        self.data = murdock.report.substitute_fields(self.data, SPECIAL_CHARS)
        if self._subs is not None:
            self.data = murdock.report.substitute_fields(self.data, self._subs)
        self._rescale_widths()
        t = '\n'
        t += '\\begin{tabular}{%s |}\n' % ' '.join(self.col_fmts)
        t += '\\hline\n'
        try:
            t += ' & '.join([
                '\multicolumn{%d}{%sc|}{%s}' % (
                    len(stable), '|' if _i == 0 else '', head.strip()) for
                _i, (head, stable) in enumerate(self.data.iteritems())])
            t += r'\\' + '\n'
        except AttributeError:
            pass
        sheads = [
            _skey for _stable in self.data.itervalues() for _skey in
            _stable.iterkeys()]
        t += ' & '.join(sheads) + r'\\' + '\n'
        t += '\\hline\n'
        i = 0
        while True:
            cols = []
            for head, subtable in self.data.iteritems():
                try:
                    cols.extend(_col[i] for _col in subtable.itervalues())
                except IndexError:
                    break
            if not cols:
                break
            t += '%s' % (' & '.join(cols)) + r'\\' + '\n'
            i += 1
        t += '\\hline\n'
        t += '\\end{tabular}\n'
        return t

    def _isnumeric(self, x):
        if self._subs is not None and x in self._subs:
            x = self._subs[x]
        if x.startswith('\\textbf') or x.startswith('\\textit'):
            x = x[8:-1]
        try:
            float(x)
        except ValueError:
            return False
        return True

    def _rescale_widths(self):
        num_cols = sum([
            len(_subtable.keys()) for _subtable in self.data.itervalues()])
        scale = 0.99 / num_cols
        fig_widths = {r'\textwidth': r'%.2f\textwidth' % scale}
        self.data = murdock.report.substitute_fields(self.data, fig_widths)
        return True

    def _set_column_formatters(self, fmts=None):
        if fmts is not None:
            self.col_fmts = fmts
        else:
            self.col_fmts = []
            for subtable in self.data.itervalues():
                self.col_fmts.append('|')
                for col in subtable.itervalues():
                    if False in (self._isnumeric(_x) for _x in col):
                        self.col_fmts.append('l')
                    else:
                        self.col_fmts.append('r')
        return True


def _escape_special_chars(data):
    return murdock.report.substitute_all(data, SPECIAL_CHARS)
