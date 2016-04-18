# coding: utf-8
# Copyright (C) 2015 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/

from __future__ import unicode_literals, absolute_import
import sys
import os
import io
import tempfile
import shutil
import contextlib
import difflib
import itertools

import sh

import urwid
import unittest
import lairucrem
import lairucrem.controller
from lairucrem.utils import monkeypatch
import sure, sure.core, sure.terminal

__all__ = ['tempdir', 'temprepo', 'mkpath']


HERE = os.path.dirname(os.path.abspath(__file__))

class mock(object):
    def __new__(cls, *args, **kwargs):
        self = super(mock, cls).__new__(cls)
        self.__newargs__ = args, kwargs
        self.called = []
        self.accessed = []
        return self
    def __setattr__(self, name, value):
        self.__dict__[name] = value
    def __getattr__(self, name):
        return self
    def __call__(self, *args, **kwargs):
        return self
    def diff(self, *args, **kwargs):
        return mock(next='bonjour')
    def __next__(self): return self
    next = __next__
    def __iter__(self):
        while True:
            yield self.__next__()


class mockscreen(mock):
    _started = True
    def get_cols_rows(self):
        return 10, 10

class mockloop(lairucrem.controller.mainloop):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('screen', mockscreen())
        super(mockloop, self).__init__(*args, **kwargs)
        
    def loop(self, did_something=True):
        self.event_loop._did_something = did_something
        self.screen._started = True
        self.event_loop._loop()

    def start(self): pass

    def stop(self): pass

    def loop(self, block=False, draw_screen=True):
        if getattr(self.event_loop, '_did_something', None) is None:
            self.event_loop._did_something = False
        self.screen._started = True
        if not block:
            def _unblocker(*a): None
            self.set_alarm_in(0.001, _unblocker)
        self.event_loop._loop()
        if draw_screen:
            self.draw_screen()


def mkpath(*paths):
    """build path by given file/folder inside the tests folder"""
    return os.path.join(HERE, *paths)

@contextlib.contextmanager
def tempdir(**kwargs):
    """Create a temporary folder that has the same live time than the
    context. Yield the temporary folder path.

    Named arguments are passed to `tempfile.mkdtemp`.
    """
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        shutil.rmtree(path)


@contextlib.contextmanager
def temprepo(**kwargs):
    """create a temporary mercurial repository and return a sh.hg object
    baked to target this repository.

    Named arguments are passed to `tempfile.mkdtemp` and `hglib.init` accordingly.
    """
    with tempdir() as path:
        sh.hg.init(path).wait()
        hg = lairucrem.repository(path).bake(
            _env={'HGRCPATH': ''},
            config='extensions.lairucremtest=%s' % mkpath('extension.py'),
            **kwargs
        ).bake(config='ui.username=test')
        hg._root = path
        yield hg

# 
# augment sure

@monkeypatch(sure.core.DeepExplanation)
def get_header(self, X, Y, suffix):
    # fix unicode stulff
    params = (sure.core.safe_repr(X), sure.core.safe_repr(Y), sure.core.text_type(suffix))
    header = u"given\nX = %s\n    and\nY = %s\n%s" % params
    return sure.terminal.yellow(header).strip()
sure.core.DeepComparison.cmp_mapping = {}


_DeepComparison_init = sure.core.DeepComparison.__init__
@monkeypatch(sure.core.DeepComparison)
def __init__(self, *args, **kwargs):
    _DeepComparison_init(self, *args, **kwargs)
    self.cmp_mapping = self.cmp_mapping.copy()
    self.cmp_mapping.update({
        dict: self.compare_dicts,
        list: self.compare_iterables,
        tuple: self.compare_iterables,
    })


@monkeypatch(sure.core.DeepComparison)
def compare_complex_stuff(self, X, Y):
    return self.cmp_mapping.get(type(X), self.compare_generic)(X, Y)


@monkeypatch(sure.core.DeepComparison)
def is_simple(self, obj):
    return isinstance(obj, (float, sure.core.integer_types))


def compare_text(X, Y):
    """compare two stringios"""
    X = X.splitlines()
    Y = Y.splitlines()
    if X == Y:
        return True
    else:
        try:
            return sure.core.DeepExplanation('\n'.join(difflib.ndiff(X, Y)))
        except UnicodeDecodeError:
            return sure.core.DeepExplanation('\n'.join(v.decode('utf-8') for v in difflib.ndiff(X, Y)))
# sure.core.DeepComparison.cmp_mapping[io.StringIO] = compare_stringio
sure.core.DeepComparison.cmp_mapping[sure.core.text_type] = compare_text
sure.core.DeepComparison.cmp_mapping[str] = compare_text


# 
# auto test

class test_contexts(unittest.TestCase):

    def test_tempdir(self):
        with tempdir() as path:
            os.path.isdir(path).must.be.true
            with io.open(os.path.join(path, 'foo'), encoding='utf-8', mode='w') as fid:
                fid.write(u'content')
            os.path.isfile(os.path.join(path, 'foo')).must.be.true
        os.path.isdir(path).must.be.false

    def test_tmprepo(self):
        with temprepo() as repo:
            repopath = str(repo.root())
            repopath.startswith(tempfile.tempdir).must.be.true
        os.path.exists(repopath).must.be.false


class test_sure(unittest.TestCase):
    def test_stringio_fails(self):
        foo = 'fooŕ'
        bar = 'barç'
        try:
            foo.must.equal(bar)
        except AssertionError as err:
            regexp = """given\nX = u'foo\\u0155'\n    and\nY = u'bar\\xe7'\n- fooŕ\n+ barç"""
            err.message.should.equal(regexp)

    def test_stringio_succeed(self):
        foo = u'fooŕ'
        bar = u'fooŕ'
        foo.must.equal(bar)

class test_extension(unittest.TestCase):
    def test_say(self):
        with temprepo() as hg:
            hg.say('hello').__unicode__().must.equal('hello')

    def test_mkcset(self):
        with temprepo() as hg:
            # simplest
            hg.mkcset('foo').wait()
            hg.log(template='{desc}').__unicode__().strip().must.equal('foo')
            hg.cat(os.path.join(hg._root, 'foo')).__unicode__().must.equal('foo')
            # with more arguments
            hg.mkcset('foo', 'some content', message='a message').wait()
            hg.log(template='{desc}', rev='tip').__unicode__().strip().must.equal('a message')
            hg.cat(os.path.join(hg._root, 'foo')).__unicode__().must.equal('some content')
