# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.tinject -- Implementation of changefile step
# :Created:   ven 22 apr 2016 21:21:00 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from pathlib import Path

from . import Step


def shorten(s, l=20):
    if len(s) > l:
        s = s[:l] + '…'
    return s.strip().replace('\n', ' ')


class Patch(object):
    def __init__(self, state, config):
        self.state = state

    def announce(self):
        raise NotImplementedError('%s should implement the announce method'
                                  % self.__class__.__name__)

    def __call__(self, content, announce_only):
        raise NotImplementedError('%s should implement the __call__ method'
                                  % self.__class__.__name__)


class AddBefore(Patch):
    def __init__(self, state, config):
        super().__init__(state, config)
        self.add = config['add']
        self.before = config['before']

    def announce(self):
        add = self.state.render_string(self.add)
        self.state.announce('  -', "add “%s” before “%s”",
                            shorten(add), shorten(self.before))

    def __call__(self, content):
        add = self.state.render_string(self.add)
        head, sep, tail = content.partition(self.before)
        return head + add + sep + tail


class AddAfter(Patch):
    def __init__(self, state, config):
        super().__init__(state, config)
        self.add = config['add']
        self.after = config['after']

    def announce(self):
        add = self.state.render_string(self.add)
        self.state.announce('  -', "add “%s” after “%s”",
                            shorten(add), shorten(self.after))

    def __call__(self, content):
        add = self.state.render_string(self.add)
        head, sep, tail = content.partition(self.after)
        return head + sep + add + tail


class InsertBetween(Patch):
    def __init__(self, state, config):
        super().__init__(state, config)
        insert = config['insert']
        if '\n' in insert:
            # Better safe than sorry: it doesn't make any sense to insert a multiline snippet,
            # as we are going to sort the block...
            if sum(1 for _ in filter(None, insert.splitlines())) > 1:
                raise ValueError('"insert" must be a single line: %r' % insert)
        else:
            insert += '\n'
        self.insert = insert
        self.between = config['between']
        self.and_ = config['and']

    def announce(self):
        insert = self.state.render_string(self.insert)
        self.state.announce('  -', "insert “%s” between “%s” and “%s”",
                            shorten(insert),
                            shorten(self.between),
                            shorten(self.and_))

    def __call__(self, content):
        insert = self.state.render_string(self.insert)
        head, start_sep, rest = content.partition(self.between)
        block, end_sep, tail = rest.partition(self.and_)
        lines = block.splitlines(True)
        lines.append(insert)
        block = ''.join(sorted(lines))
        return head + start_sep + block + end_sep + tail


class ChangeFile(Step):
    def __init__(self, state, config):
        super().__init__(state, config)
        directory = state.render_string(config.get('directory', '.'))
        filename = state.render_string(config['filename'])
        self.filename = Path(directory) / filename
        self.changes = []
        for change in config['changes']:
            if 'add' in change:
                if 'before' in change:
                    self.changes.append(AddBefore(state, change))
                    continue
                elif 'after' in change:
                    self.changes.append(AddAfter(state, change))
                    continue
            elif 'insert' in change:
                if 'between' in change and 'and' in change:
                    self.changes.append(InsertBetween(state, change))
                    continue

            raise ValueError('Unrecognized change: %r' % change)

    def announce(self):
        self.state.announce('*', "Change file %s", self.filename)
        for change in self.changes:
            change.announce()

    def __call__(self, defaults):
        content = self.filename.read_text('utf-8')
        for change in self.changes:
            content = change(content)
        if not self.state.dry_run:
            self.filename.write_text(content, 'utf-8')
