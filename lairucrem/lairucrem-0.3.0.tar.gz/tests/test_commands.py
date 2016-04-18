# -*- encoding: utf-8 -*-
#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""UI widgets for lairucrem."""

from __future__ import unicode_literals, absolute_import, nested_scopes

from unittest import TestCase
import sure
import io
import os
from subprocess import CalledProcessError

import urwid

from lairucrem import commands
from .test_utils import temprepo


class test_cmd(TestCase):
    def test_append_no_args(self):
        registry = []
        @commands.cmd(_registry=registry)
        def foo(repo, cset, _cache):
            """description

            information
            """
        registry.should.equal([(foo, foo.__name__)])

        @commands.cmd(_registry=registry)
        def bar(repo, cset, _cache):
            """description

            information
            """
        registry.should.equal([
            (foo, foo.__name__),
            (bar, bar.__name__),
        ])

    def test_append_specific_name(self):
        registry = []
        @commands.cmd(name="bar", _registry=registry)
        def foo(repo, cset, _cache):
            """description

            information
            """
        registry.should.equal([(foo, 'bar')])

    def test_append_replace_existing(self):
        registry = []
        @commands.cmd(_registry=registry)
        def foo(repo, cset, _cache):
            """description

            information
            """
        registry.should.equal([(foo, foo.__name__)])

        @commands.cmd(replace=(foo, 'foo'), _registry=registry)
        def bar(repo, cset, _cache):
            """description

            information
            """
        registry.should.equal([
            (bar, bar.__name__),
        ])


def test_get_valid_actions():
    registry = []
    @commands.cmd(_registry=registry)
    def foo(repo, cset, _cache):
        yield False
    registry.should.equal([(foo, foo.__name__)])

    @commands.cmd(_registry=registry)
    def bar(repo, cset, _cache):
        yield True

    results = list(commands.get_valid_actions(None, None, registry=registry))
    len(results).should.be(1)


class test_cmd_commit(TestCase):
    def test_activation(self):
        with temprepo() as repo:
            cset = repo.mkcset('foo')
            next(commands.shelve(repo, '', {})).should.be.falsy
            with io.open(os.path.join(repo._root, 'foo'), 'w', encoding='utf8') as fid:
                fid.write('draft')
            next(commands.commit(repo, cset, {})).should.be.falsy
            next(commands.commit(repo, '', {})).should.be.truthy

    def test_commit(self):
        with temprepo() as repo:
            cset = repo.mkcset('foo')
            with io.open(os.path.join(repo._root, 'foo'), 'w', encoding='utf8') as fid:
                fid.write('draft')
            action = commands.commit(repo, '', {})
            try:
                for dummy in action:
                    pass
            except CalledProcessError as err: # it fails because we are not interactive
                'commit'.should.be.within(err.cmd)
                '--interactive'.should.be.within(err.cmd)
                '--config=experimental.crecord=true'.should.be.within(err.cmd)


class test_cmd_amend(TestCase):
    def test_activation(self):
        with temprepo() as repo:
            cset = repo.mkcset('foo')
            next(commands.shelve(repo, '', {})).should.be.falsy
            with io.open(os.path.join(repo._root, 'foo'), 'w', encoding='utf8') as fid:
                fid.write('draft')
            next(commands.amend(repo, cset, {})).should.be.falsy
            next(commands.amend(repo, '', {})).should.be.truthy

    def test_amend(self):
        with temprepo() as repo:
            cset = repo.mkcset('foo')
            with io.open(os.path.join(repo._root, 'foo'), 'w', encoding='utf8') as fid:
                fid.write('draft')
            action = commands.amend(repo, '', {})
            try:
                for dummy in action:
                    pass
            except CalledProcessError as err: # it fails because we are not interactive
                'commit'.should.be.within(err.cmd)
                '--amend'.should.be.within(err.cmd)
                '--interactive'.should.be.within(err.cmd)
                '--config=experimental.crecord=true'.should.be.within(err.cmd)


class test_cmd_addremove(TestCase):

    def test_activation(self):
        with temprepo() as repo:
            cset = repo.mkcset('foo')
            next(commands.addremove(repo, cset, {})).should.be.falsy
            next(commands.addremove(repo, '', {})).should.be.falsy

            os.remove(os.path.join(repo._root, 'foo'))
            next(commands.addremove(repo, '', {})).should.be.truthy

            repo.revert(all=True)
            next(commands.addremove(repo, '', {})).should.be.falsy
            with io.open(os.path.join(repo._root, 'bar'), 'w', encoding='utf8') as fid:
                fid.write('draft')
            next(commands.addremove(repo, '', {})).should.be.truthy

    def test_apply(self):
        with temprepo() as repo:
            cset = repo.mkcset('foo')
            with io.open(os.path.join(repo._root, 'bar'), 'w', encoding='utf8') as fid:
                fid.write('draft')
            os.remove(os.path.join(repo._root, 'foo'))
            action = commands.addremove(repo, '', {})
            next(action).should.be.truthy
            dialog = (action).send(action)
            dialog.should.be.an(urwid.Widget)
            dialog._emit('selected', ['apply', [0, 1]])
            for dummy in action:
                pass
            set(unicode(repo.status()).splitlines()).should.equal(set(['R foo', 'A bar']))

    def test_fix(self):
        with temprepo() as repo:
            cset = repo.mkcset('foo')
            with io.open(os.path.join(repo._root, 'bar'), 'w', encoding='utf8') as fid:
                fid.write('draft')
            os.remove(os.path.join(repo._root, 'foo'))
            action = commands.addremove(repo, '', {})
            next(action).should.be.truthy
            dialog = (action).send(action)
            dialog.should.be.an(urwid.Widget)
            dialog._emit('selected', ['fix', [0, 1]])
            for dummy in action:
                pass
            unicode(repo.status()).strip().should.be.falsy


class test_shelve(TestCase):
    def test_activation(self):
        with temprepo() as repo:
            cset = repo.mkcset('foo')
            next(commands.shelve(repo, '', {})).should.be.falsy
            with io.open(os.path.join(repo._root, 'foo'), 'w', encoding='utf8') as fid:
                fid.write('draft')
            next(commands.shelve(repo, cset, {})).should.be.falsy
            next(commands.shelve(repo, '', {})).should.be.truthy

    def test_shelve(self):
        with temprepo() as repo:
            cset = repo.mkcset('foo')
            with io.open(os.path.join(repo._root, 'foo'), 'w', encoding='utf8') as fid:
                fid.write('draft')
            action = commands.shelve(repo, '', {})
            try:
                for dummy in action:
                    pass
            except CalledProcessError as err: # it fails because we are not interactive
                'shelve'.should.be.within(err.cmd)
                '--interactive'.should.be.within(err.cmd)
                '--config=extensions.hgext.shelve='.should.be.within(err.cmd)

    def test_unshelve(self):
        with temprepo() as repo:
            cset = repo.mkcset('foo')
            with io.open(os.path.join(repo._root, 'foo'), 'w', encoding='utf8') as fid:
                fid.write('draft')
            next(repo.shelve(config='extensions.hgext.shelve='))
            action = commands.unshelve(repo, '', {})
            action.send(None)
            dialog = action.send(action)
            dialog.should.be.an(urwid.Widget)
            dialog._emit('selected', 0)
            unicode(repo.status()).strip().should.equal('M foo')
        

class test_update(TestCase):
    def test_activation(self):
        with temprepo() as repo:
            cset1 = unicode(repo.mkcset('foo'))
            cset2 = unicode(repo.mkcset('bar'))
            next(commands.update(repo, '', {})).should.be.falsy
            next(commands.update(repo, cset2, {})).should.be.falsy
            next(commands.update(repo, cset1, {})).should.be.truthy

    def test_update(self):
        with temprepo() as repo:
            cset1 = unicode(repo.mkcset('foo'))
            cset2 = unicode(repo.mkcset('bar'))
            action = commands.update(repo, cset1, {})
            list(action)
            next(repo.identify())[:8].should.equal(cset1.split(':', 1)[1][:8])


class test_histedit(TestCase):
    def test_activation(self):
        with temprepo() as repo:
            cset1 = unicode(repo.mkcset('foo'))
            cset2 = unicode(repo.mkcset('bar'))
            next(commands.histedit(repo, '', {})).should.be.falsy
            next(commands.histedit(repo, cset2, {})).should.be.falsy
            next(commands.histedit(repo, cset1, {})).should.be.truthy

            # no histedit on durty
            with io.open(os.path.join(repo._root, 'foo'), 'w', encoding='utf8') as fid:
                fid.write('draft')

            next(commands.histedit(repo, cset1, {})).should.be.falsy

    def test_histedit(self):
        with temprepo() as repo:
            cset1 = unicode(repo.mkcset('foo'))
            cset2 = unicode(repo.mkcset('bar'))
            action = commands.histedit(repo, cset1, {})
            next(action)
            try:
                list(action)
            except CalledProcessError as err: # it fails because we are not interactive
                cmd = ' '.join(err.cmd)
                'histedit'.should.be.within(cmd)
                '--config=extensions.hgext.histedit='.should.be.within(cmd)
                ('--rev=%s' % cset1).should.be.within(cmd)


class test_rebase(TestCase):

    def build_repo(self, repo):
        yield unicode(repo.mkcset('foo'))

        yield unicode(repo.mkcset('bar'))
        unicode(repo.phase(public=True, rev='1'))
        yield unicode(repo.mkcset('barbar'))

        unicode(repo.update('0'))
        yield unicode(repo.mkcset('to', quiet=True))
        yield unicode(repo.mkcset('toto'))
        yield unicode(repo.mkcset('tototo'))
        yield unicode(repo.mkcset('totototo'))
        unicode(repo.update('4'))


    def _check_activation(self, cmd):
        with temprepo() as repo:
            csets = list(self.build_repo(repo))

            # no rebase for durty
            next(cmd(repo, '', {})).should.be.falsy

            # no rebase for parent
            next(cmd(repo, csets[3], {})).should.be.falsy

            # rebase ok for other branch if not public
            next(cmd(repo, csets[1], {})).should.be.falsy
            next(cmd(repo, csets[2], {})).should.be.truthy

            # # rebase ok for descendants
            # cmd(repo, csets[6], {}).should.be.truthy

    def test_rebase_activation(self):
        self._check_activation(commands.rebase)

    def test_rebase_one_activation(self):
        self._check_activation(commands.rebase_one)

    def test_graft_activation(self):
        self._check_activation(commands.graft)

    def test_reabse(self):
        with temprepo() as repo:
            csets = list(self.build_repo(repo))
            list(commands.rebase(repo, csets[2], {}))
            result = unicode(repo.log(template='{rev}:{node} ')).split()
            csets.pop(2)
            result[1:].should.equal(list(reversed(csets)))

    def test_reabse_one(self):
        with temprepo() as repo:
            csets = list(self.build_repo(repo))
            list(commands.rebase_one(repo, csets[2], {}))
            result = unicode(repo.log(template='{rev}:{node} ')).split()
            csets.pop(2)
            result[1:].should.equal(list(reversed(csets)))

    def test_graft(self):
        with temprepo() as repo:
            csets = list(self.build_repo(repo))
            list(commands.graft(repo, csets[2], {}))
            result = unicode(repo.log(template='{rev}:{node} ')).split()
            result[1:].should.equal(list(reversed(csets)))



class test_draft(TestCase):
    def test_activation(self):
        with temprepo() as repo:
            cset = unicode(repo.mkcset('foo'))
            unicode(repo.phase(rev=cset, force=True, secret=True))

            # durty could not be draft
            next(commands.draft(repo, '', {})).should.be.falsy

            # secret could be draft
            next(commands.draft(repo, cset, {})).should.be.truthy

            # not needed if already draft
            unicode(repo.phase(rev=cset, force=True, draft=True))
            next(commands.draft(repo, cset, {})).should.be.falsy

            # public should stay immutable (users will use their own
            # command if they really want it)
            unicode(repo.phase(rev=cset, force=True, public=True))
            next(commands.draft(repo, cset, {})).should.be.falsy

    def test_draft(self):
        with temprepo() as repo:
            cset = unicode(repo.mkcset('foo'))
            unicode(repo.phase(rev=cset, force=True, secret=True))
            action = commands.draft(repo, cset, {})
            list(action)
            'draft'.should.be.within(unicode(repo.phase(cset)))

class test_public(TestCase):
    def test_activation(self):
        with temprepo() as repo:
            cset = unicode(repo.mkcset('foo'))
            unicode(repo.phase(rev=cset, force=True, draft=True))

            # durty could not be public
            next(commands.public(repo, '', {})).should.be.falsy

            # secret could be public
            next(commands.public(repo, cset, {})).should.be.truthy

            # not needed if already public
            unicode(repo.phase(rev=cset, force=True, public=True))
            next(commands.public(repo, cset, {})).should.be.falsy

            # public should stay immutable (users will use their own
            # command if they really want it)
            unicode(repo.phase(rev=cset, force=True, public=True))
            next(commands.public(repo, cset, {})).should.be.falsy

    def test_public(self):
        with temprepo() as repo:
            cset = unicode(repo.mkcset('foo'))
            unicode(repo.phase(rev=cset, force=True, draft=True))
            action = commands.public(repo, cset, {})
            list(action)
            'public'.should.be.within(unicode(repo.phase(cset)))


class test_push(TestCase):
    def test_activation(self):
        with temprepo() as repo:
            # durty could not be pushed
            next(commands.push(repo, '', {})).should.be.falsy

            cset = unicode(repo.mkcset('foo'))

            # secret are local only
            unicode(repo.phase(rev=cset, force=True, secret=True))
            next(commands.push(repo, cset, {})).should.be.falsy

            # we do not check remote because it is too long
            unicode(repo.phase(rev=cset, force=True, draft=True))
            next(commands.push(repo, cset, {})).should.be.truthy

    def test_push_simple_dest(self):
        with temprepo() as orig, temprepo() as dest:
            cset1 = unicode(orig.mkcset('foo'))
            cset2 = unicode(orig.mkcset('bar'))
            cset3 = unicode(orig.mkcset('babar'))
            with io.open(os.path.join(orig._root, '.hg', 'hgrc'), 'w', encoding='utf8') as fid:
                fid.writelines(['[paths]\n', 'default=%s' % dest._root])
            list(commands.push(orig, cset1, {}))
            unicode(dest.log(template='{rev}:{node}')).should.equal(cset1)
            list(commands.push(orig, cset3, {}))
            unicode(dest.log(template='{rev}:{node}')).should.equal(''.join((cset3, cset2, cset1)))

    def test_push_multiple_dest(self):
        with temprepo() as orig, temprepo() as dest1, temprepo() as dest2:
            cset1 = unicode(orig.mkcset('foo'))
            cset2 = unicode(orig.mkcset('bar'))
            cset3 = unicode(orig.mkcset('babar'))
            with io.open(os.path.join(orig._root, '.hg', 'hgrc'), 'w', encoding='utf8') as fid:
                fid.writelines(['[paths]\n',
                                'default = %s\n' % dest1._root,
                                'review = %s\n' % dest2._root])
            # push on the first dest
            action = commands.push(orig, cset1, {})
            action.send(None)
            dialog = action.send(action)
            dialog.should.be.an(urwid.Widget)
            dialog._emit('selected', 0)
            list(action)
            unicode(dest1.log(template='{rev}:{node}')).should.equal(cset1)
            unicode(dest2.log(template='{rev}:{node}')).strip().should.be.falsy
            # push on the second dest
            action = commands.push(orig, cset3, {})
            action.send(None)
            dialog = action.send(action)
            dialog.should.be.an(urwid.Widget)
            dialog._emit('selected', 1)
            list(action)
            unicode(dest1.log(template='{rev}:{node}')).should.equal(cset1)
            unicode(dest2.log(template='{rev}:{node}')).should.equal(''.join((cset3, cset2, cset1)))



class test_revert(TestCase):
    def test_activation(self):
        with temprepo() as repo:
            next(commands.revert(repo, '', {})).should.be.falsy
            cset1 = unicode(repo.mkcset('foo'))
            cset2 = unicode(repo.mkcset('bar'))
            next(commands.revert(repo, cset1, {})).should.be.truthy
            with io.open(os.path.join(repo._root, 'foo'), 'w', encoding='utf8') as fid:
                fid.write('draft')
            next(commands.revert(repo, '', {})).should.be.truthy

    def test_cwd(self):
        with temprepo() as repo:
            cset1 = unicode(repo.mkcset('foo'))
            with io.open(os.path.join(repo._root, 'foo'), 'w', encoding='utf8') as fid:
                fid.write('draft')
            list(commands.revert(repo, '', {}))
            unicode(repo.status()).strip().should.equal('? foo.orig')

    def test_cset(self):
        with temprepo() as repo:
            cset1 = unicode(repo.mkcset('foo', 'initial'))
            cset2 = unicode(repo.mkcset('foo', 'modified'))
            list(commands.revert(repo, cset1, {}))
            unicode(repo.status()).strip().should.equal('M foo')


class test_edit_description(TestCase):
    def test_activation(self):
        with temprepo() as repo:
            cset1 = unicode(repo.mkcset('foo'))
            next(commands.edit_description(repo, '', {})).should.be.falsy
            next(commands.edit_description(repo, cset1, {})).should.be.truthy

    def test_edit_description(self):
        raise self.skipTest('editor will fail')
