"""
This is a high level API that wraps the core features of the
application and let you use them in your plugins. The different plugin
interfaces and a set of utility widgets are also defined here.

This API is considered stable, care is taken to not break backward
compatibility. This package is covered by unit tests and care is taken to keep
the coverage as high as possible.

.. warning:: This API will be considered stable once HackEdit hits the beta
             status. You have been warned...



.. note:: Most of the API functions need a reference to the main window,
    which is the central object of the application. In order to simplify the
    API and since those functions are meant for writing plugins and plugins
    already hold a reference to the main window, we decided to remove the
    `main_window` parameter from every function and retrieve it automatically
    by inspecting the stack frames (we retrieve the `_window` attribute from
    the calling object).

    If you're calling the api functions outside of a plugin, the active window
    will be used instead (unless you have a reference to the main window named
    `_window`).

    This makes the API easier to use, i.e. you don't have to know anything
    about the main window and its underlying implementation. This also opens
    up lots of possibilities: you can use the api from within HackEdit itself,
    e.g. through the developer console plugin...

"""
from . import editor
from . import events
from . import gettext
from . import index
from . import interpreters
from . import plugins
from . import project
from . import shortcuts
from . import signals
from . import special_icons
from . import system
from . import tasks
from . import utils
from . import versions
from . import widgets
from . import window


__all__ = [
    'editor',
    'events',
    'gettext',
    'index',
    'interpreters',
    'plugins',
    'project',
    'shortcuts',
    'signals',
    'special_icons',
    'system',
    'tasks',
    'utils',
    'versions',
    'widgets',
    'window'
]
