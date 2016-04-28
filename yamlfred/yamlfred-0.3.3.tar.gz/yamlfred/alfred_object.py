# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os.path
import uuid
from yamlfred.utils import remove_default, merge_dicts

from yamlfred.utils import Include

defaults = {
    'alfred.workflow.output.notification': {
        'config': {'removeextension': False, 'output': 0, 'lastpathcomponent': False, 'onlyshowifquerypopulated': False, 'sticky': False},
        'version': 0,
    },
    'alfred.workflow.trigger.hotkey': {
        'config': {'leftcursor': False, 'argument': 0, 'relatedAppsMode': 0, 'action': 0, 'hotkey': 0, 'hotstring': '', 'hotmod': 0, 'modsmode': 0},
        'version': 1, },
    'alfred.workflow.action.openfile': {
        'config': {},
        'version': 1,
    },
    'alfred.workflow.input.keyword': {
        'config': {'argumenttype': 0, 'withspace': True},
        'version': 0,
    },
    'alfred.workflow.trigger.external': {
        'config': {},
        'version': 0,
    },
    'alfred.workflow.output.largetype': {
        'version': 0,
    },
    'alfred.workflow.action.revealfile': {
        'version': 0,
    },
    'alfred.workflow.input.filefilter': {
        'config': {'scopes': [], 'includesystem': False, 'withspace': True, 'anchorfields': True, 'daterange': 0, 'types': []},
        'version': 0,
    },
    'alfred.workflow.input.scriptfilter': {
        'config': {'withspace': True, 'escaping': 102, 'script': '', 'argumenttype': 0, 'type': 0,
                   'queuedelaycustom': 3, 'queuedelayimmediatelyinitially': True, 'queuedelaymode': 0, 'queuemode': 1},
        'version': 0,
    },
    'alfred.workflow.action.browseinalfred': {
        'config': {},
        'version': 0,
    },
    'alfred.workflow.trigger.action': {
        'config': {'filetypes': [], 'acceptsmulti': False},
        'version': 0,
    },
    'alfred.workflow.output.clipboard': {
        'config': {'clipboardtext': '', 'autopaste': False},
        'version': 0, },
    'alfred.workflow.output.script': {
        'config': {'escaping': 102, 'type': 0, 'script': '', 'concurrently': False},
        'version': 0, },
    'alfred.workflow.action.launchfiles': {
        'config': {'paths': [], 'toggle': False},
        'version': 0,
    },
    'alfred.workflow.trigger.contact': {
        'config': {},
        'version': 0,
    },
    'alfred.workflow.action.systemwebsearch': {
        'config': {},
        'version': 0,
    },
    'alfred.workflow.trigger.fallback': {
        'config': {},
        'version': 0,
    },
    'alfred.workflow.action.openurl': {
        'config': {'utf8': True, 'plusspaces': False},
        'version': 0,
    },
    'alfred.workflow.action.systemcommand': {
        'config': {'command': 0, 'confirm': False},
        'version': 1,
    },
    'alfred.workflow.action.itunescommand': {
        'config': {'command': 0},
        'version': 0,
    },
    'alfred.workflow.action.script': {
        'config': {'escaping': 102, 'type': 0, 'script': '', 'concurrently': False},
        'version': 0,
    },
    'alfred.workflow.action.applescript': {
        'config': {'cachescript': False, 'applescript': ''},
        'version': 0,
    },
    'alfred.workflow.action.terminalcommand': {
        'config': {'escaping': 0},
        'version': 0,
    },
    'alfred.workflow.trigger.remote': {
        'config': {'argumenttype': 0, 'workflowonly': False},
        'version': 0,
    },
}


class AlfredObject(object):

    def __init__(self, dic):
        self.type = dic['type']
        default = defaults[self.type] if self.type in defaults else {}
        self.prop = merge_dicts(default, dic)
        if 'uid' not in self.prop:
            self.prop['uid'] = uuid.uuid4()
        self.script_type = None
        if self.type == 'alfred.workflow.action.applescript':
            self.script_type = 'applescript'
        elif self.type in ['alfred.workflow.input.scriptfilter',
                           'alfred.workflow.output.script',
                           'alfred.workflow.action.script']:
            self.script_type = 'script'
        return

    def dump(self, script_dir='.'):
        default = defaults[self.type] if self.type in defaults else {}
        prop = remove_default(self.prop, default)
        if self.script_type:
            path = os.path.join(script_dir, self.prop['uid'])
            with open(path, 'w') as f:
                script = self.prop['config'].get(self.script_type)
                f.write(script)
            prop['config'][self.script_type] = Include(path)
        return prop
