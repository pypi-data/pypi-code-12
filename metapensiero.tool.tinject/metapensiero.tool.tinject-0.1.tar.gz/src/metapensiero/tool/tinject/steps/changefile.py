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
        self.add = config['add'] + '\n'
        self.before = config['before'] + '\n'

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
        self.add = config['add'] + '\n'
        self.after = config['after'] + '\n'

    def announce(self):
        add = self.state.render_string(self.add)
        self.state.announce('  -', "add “%s” after “%s”",
                            shorten(add), shorten(self.after))

    def __call__(self, content):
        add = self.state.render_string(self.add)
        head, sep, tail = content.partition(self.after)
        return head + sep + add + tail


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
                elif 'after' in change:
                    self.changes.append(AddAfter(state, change))
                else:
                    raise ValueError('Unrecognized change: %r' % change)
            else:
                raise ValueError('Unrecognized change: %r' % change)

    def announce(self):
        self.state.announce('*', "Change file %s", self.filename)
        for change in self.changes:
            change.announce()

    def __call__(self):
        content = self.filename.read_text('utf-8')
        for change in self.changes:
            content = change(content)
        if not self.state.dry_run:
            self.filename.write_text(content, 'utf-8')
