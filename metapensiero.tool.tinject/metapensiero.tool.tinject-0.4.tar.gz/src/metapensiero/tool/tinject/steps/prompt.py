# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.tinject -- Prompt implementation
# :Created:   gio 21 apr 2016 18:49:11 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

import inquirer

from . import Step


class Prompt(Step):
    def __init__(self, state, config):
        super().__init__(state, config)

        questions = self.questions = []

        for question in config:
            items = question.items()
            assert len(items) == 1
            for name, details in items:
                pass
            opts = dict(details)
            if 'message' not in details:
                opts['message'] = name.capitalize()
            else:
                opts['message'] = details['message']
            opts['message'] += ' (%s)' % name
            kind = opts.pop('kind', 'text')
            if kind == 'text':
                prompt = inquirer.Text(name, **opts)
            elif kind == 'password':
                prompt = inquirer.Password(name, **opts)
            elif kind == 'checkbox':
                prompt = inquirer.Checkbox(name, **opts)
            elif kind == 'confirm':
                prompt = inquirer.Confirm(name, **opts)
            elif kind == 'list':
                prompt = inquirer.List(name, **opts)
            else:
                raise ValueError('Unknown question kind: %s' % kind)

            questions.append(prompt)

    def announce(self):
        pass

    def __call__(self, defaults):
        result = inquirer.prompt(self.questions, answers=defaults)
        if result is None:
            # inquirer.prompt catches KeyboardInterrupt and returns None
            raise KeyboardInterrupt
        return result
