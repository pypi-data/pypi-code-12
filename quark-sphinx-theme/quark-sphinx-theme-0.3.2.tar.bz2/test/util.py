# -*- coding: utf-8 -*-
# This file is part of quark-sphinx-theme.
# Copyright (c) 2016 Felix Krull <f_krull@gmx.de>
# Released under the terms of the BSD license; see LICENSE.

from __future__ import print_function

from io import open
import os
import shutil
from subprocess import Popen, STDOUT, PIPE
import tempfile

import html5lib
try:
    import tinycss
except ImportError:
    tinycss = None


class ExtraAsserts(object):
    def assertBases(self, cls, *bases):
        for base in bases:
            self.assertTrue(issubclass(cls, base))

    def assertCSSValid(self, filename_or_fobj, encoding=None, auto_skip=True):
        if not tinycss and auto_skip:
            self.skipTest('tinycss not available')

        if hasattr(filename_or_fobj, 'read'):
            source = filename_or_fobj.read()
        else:
            with open(filename_or_fobj, 'r', encoding=encoding) as fobj:
                source = fobj.read()
        parser = tinycss.make_parser()
        css = parser.parse_stylesheet(source)
        lines = source.split('\n')
        errors = []
        for err in css.errors:
            try:
                errors.append('  %s [%s]\n' % (err, lines[err.line - 1]))
            except IndexError:
                errors.append('  %s\n' % err)
        self.assertEqual(len(css.errors), 0, 'CSS errors:\n' + ''.join(errors))


def run_sphinx(source_dir, build_dir, builder='html', extra_config={}, tags=[],
               sphinx_build='sphinx-build'):
    args = [sphinx_build, '-b', builder]
    for k, v in extra_config.items():
        args.extend(['-D', '%s=%s' % (k, v)])
    for tag in tags:
        args.extend(['-t', tag])
    args.extend([source_dir, build_dir])

    popen = Popen(args, stdout=PIPE, stderr=STDOUT)
    stdout, _ = popen.communicate()
    if popen.returncode != 0:
        raise Exception('%s returned non-zero exit status %s\n'
                        '--- Output:\n%s----' %
                        (args, popen.returncode,
                         stdout.decode('ascii', errors='replace')))


class SphinxBuildFixture(ExtraAsserts):
    source_dir = None
    builder = 'html'
    config = {}
    tags = []

    build_dir = None

    @classmethod
    def setUpClass(cls):
        if not cls.source_dir:
            raise Exception('source_dir not set')
        cls.build_dir = tempfile.mkdtemp(prefix='tmp-sphinx-build-test-')
        try:
            run_sphinx(cls.source_dir, cls.build_dir, cls.builder, cls.config,
                       cls.tags)
        except Exception:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        if cls.build_dir:
            shutil.rmtree(cls.build_dir, True)
            cls.build_dir = None

    def read_document(self, name):
        path = os.path.join(self.build_dir, *name.split('/')) + '.html'
        with open(path, 'rb') as f:
            return html5lib.parse(f, namespaceHTMLElements=False)

    def assertHasElement(self, doc, path, n=1):
        self.assertEqual(len(list(doc.findall(path))), n)

    def assertNotElement(self, doc, path):
        self.assertHasElement(doc, path, 0)

    def assertSphinxCSSValid(self, basename, encoding='utf-8', auto_skip=True):
        self.assertCSSValid(os.path.join(self.build_dir, '_static', basename),
                            encoding=encoding,
                            auto_skip=auto_skip)


def with_document(docname):
    def wrap1(func):
        def wrap2(self, *args, **kwargs):
            func(self, self.read_document(docname), *args, **kwargs)
        return wrap2
    return wrap1


def with_elements(docname, xpath_expr, n=None):
    def wrap1(func):
        def wrap2(self, *args, **kwargs):
            elems = list(self.read_document(docname).findall(xpath_expr))
            if n is not None and len(elems) != n:
                raise AssertionError('expected %s element(s), got %s' %
                                     (n, len(elems)))
            elif len(elems) == 0:
                raise AssertionError('no elements')
            func(self, elems, *args, **kwargs)
        return wrap2
    return wrap1
