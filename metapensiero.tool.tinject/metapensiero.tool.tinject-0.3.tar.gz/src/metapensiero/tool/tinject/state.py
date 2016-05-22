# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.tinject -- Global state
# :Created:   ven 22 apr 2016 08:40:54 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

import jinja2

from .config import Config
from .steps import run_steps


class State(object):
    def __init__(self, verbose, dry_run, overwrite, configfile):
        self.verbose = verbose
        self.dry_run = dry_run
        self.overwrite = overwrite
        self.configfile = configfile
        self.config = Config.from_yaml(configfile)
        jopts = dict(block_start_string="<<",
                     block_end_string=">>",
                     variable_start_string="«",
                     variable_end_string="»",
                     keep_trailing_newline=True,
                     extensions=["jinja2_time.TimeExtension"])
        if 'jinja' in self.config.globals:
            if jopts != self.config.globals['jinja']:
                jopts.update(self.config.globals['jinja'])
                self.config.globals['jinja'] = jopts
            else:
                del self.config.globals['jinja']
        self.jinja = jinja2.Environment(**jopts)
        self.answers = {}

    def announce(self, decorator, msg, *args):
        if self.verbose or self.dry_run:
            if args:
                msg = msg % args
            if decorator == '=':
                msg = ' ' + msg
                decorator = decorator * (len(msg)+1)
                print("\n%s\n%s\n%s" % (decorator, msg, decorator))
            elif decorator == '-':
                decorator = decorator * len(msg)
                print("\n%s\n%s" % (msg, decorator))
            else:
                print("\n%s %s" % (decorator, msg))

    def __call__(self):
        if 'steps' in self.config.globals:
            run_steps(self, self.config.globals['steps'])

    def render_params(self, others):
        params = {}
        params.update(self.answers)
        params.update(others)
        template = self.jinja.from_string
        again = True
        while again:
            again = False
            for p in params:
                v = params[p]
                if isinstance(v, str):
                    v = template(v).render(**params)
                    if v != params[p]:
                        params[p] = v
                        again = True
        return params

    def render_string(self, string, **kwargs):
        template = self.jinja.from_string(string)
        return template.render(**self.render_params(kwargs))

    def render_file_content(self, filename, content, description, **kwargs):
        template = self.jinja.from_string(content)

        suffix = filename.suffix
        header = 'Undefined header'
        if suffix:
            suffix = suffix[1:]
            headers = self.config.globals.get('headers')
            if headers and suffix in headers:
                header = self.render_string(headers[suffix], filename=filename)
                if description:
                    description = self.render_string(description)
                    header = header.format(file_description=description)

        return template.render(header=header, **self.render_params(kwargs))
