# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.tinject -- Configuration details
# :Created:   gio 21 apr 2016 18:22:20 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from io import open
from pathlib import Path

import yaml


def include(loader, node):
    path = loader.construct_scalar(node)
    fullpath = include.basedir / path
    return fullpath.read_text('utf-8')

yaml.add_constructor('!include', include)


class Config(object):
    @classmethod
    def from_yaml(cls, fname):
        include.basedir = Path(fname).parent
        with open(fname, 'r', encoding='utf-8') as stream:
            content = yaml.load_all(stream)
            globals = next(content)
            try:
                actions = next(content)
            except StopIteration:
                actions = globals
                globals = None
        return cls(globals, actions)

    def __init__(self, globals, actions):
        self.globals = globals
        self.actions = actions

    def write(self, output):
        with open(output, 'w', encoding='utf-8') as stream:
            yaml.dump_all([self.globals, self.actions], stream,
                          allow_unicode=True,
                          default_style="|",
                          default_flow_style=False)
