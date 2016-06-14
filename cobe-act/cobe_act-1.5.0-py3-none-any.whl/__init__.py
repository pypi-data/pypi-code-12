"""The Abilisoft Common Tools.

This provides a collection of tools common for many Abilisoft
projects.

"""

import apipkg as _apipkg
import pkg_resources as _pkg_resources


__version__ = _pkg_resources.require('cobe-act')[0].version


_APISPEC = {
    'AppBase': '._appbase:AppBase',
    'ApplicationExit': '._appbase:ApplicationExit',
    'FatalError': '._appbase:FatalError',
    'fsloc': '._resources:FsDirectories',
    'log': {
        'LogLevelAction': '._log:LogLevelAction',
        'setup_logbook': '._log:setup_logbook',
    },
    'mpack': '._msgpack:mpack',
    'munpack': '._msgpack:munpack',
    'zkit': {
        'new_context': '._zkit:new_context',
        'StreamEvents': '._zkit:StreamEvents',
        'TimerABC': '._zkit:TimerABC',
        'SimpleTimer': '._zkit:SimpleTimer',
        'EventStream': '._zkit:EventStream',
        'MessageStream': '._zkit:MessageStream',
    },
}


_apipkg.initpkg(__name__, _APISPEC)
