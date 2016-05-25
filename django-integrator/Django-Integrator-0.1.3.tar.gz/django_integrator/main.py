"""
Main module.
"""

import importlib
import os

MERGABLES = ['INSTALLED_APPS', 'MIDDLEWARE_CLASSES', 'TEMPLATES']
_PATTERNS = []

def _listmerge(source, target):
    "Merges items from the source list into the target list"
    # If an item in source is already in target, then the item before it will be
    # inserted before in the target, for example a source of
    # source = [nil, one, last]
    # target = [first, one, two]
    #
    # will result in:
    # target = [first, nil, one, two, last]
    items = source[::-1]
    index = None
    while len(items) > 0:
        item = items.pop(0)
        if item in target:
            index = target.index(item)
        elif index is None:
            target.append(item)
        else:
            target.insert(index, item)
            index = None


class _Importer(object):
    "Imports django apps and merges settings."
    def __init__(self):
        self.settings = {'ORIGIN':{}}
        self.settings['TARGET'] = \
                     self.import_(os.environ['DJANGO_SETTINGS_MODULE']).__dict__
        self._first_merge = True

    def merge(self, additional_settings, path):
        "Merge additional_settings into globals()."
        for key in additional_settings.__dict__:
            if key.startswith('_'):
                continue

            value = additional_settings.__dict__[key]

            if key == 'URLCONF':
                path = path.split('.', 1)[0]
                _PATTERNS.append(path + '.' + value)

            if key in MERGABLES:
                _listmerge(value, self.settings['TARGET'][key])
                continue

            if key in self.settings['TARGET'] and self._first_merge:
                self.settings['ORIGIN'][key] = self.settings['TARGET'][key]

            self.settings['TARGET'][key] = value

        if self._first_merge:
            self._first_merge = False

    def restore(self, key):
        "Restore value from original"
        self.settings['TARGET'][key] = self.settings['ORIGIN'][key]

    def import_(self, module_path_string):
        "Import using the module_path_string"
        self.settings[module_path_string] =\
                                     importlib.import_module(module_path_string)
        return self.settings[module_path_string]

    def __call__(self, application_path):
        "Import using the module_path_string and merge into settings"
        self.settings['TARGET']['INSTALLED_APPS'].append(application_path)
        settings_path = application_path + '.settings'
        settings = self.import_(settings_path)
        self.merge(settings, settings_path)

_IMPORTER = _Importer()

def add_application(application_dot_path):
    """Import the application by the given dot path.
    If the application has a settings file/module, merge it in.
    """
    _IMPORTER(application_dot_path)

def add_settings(settings_dot_path):
    "Merge the settings in."
    settings = _IMPORTER.import_(settings_dot_path)
    _IMPORTER.merge(settings, settings_dot_path)


def add_urlpatterns(patterns):
    "Add urlpatterns to given patterns"
    for module_path in _PATTERNS:
        module = importlib.import_module(module_path)

        for entry in module.urlpatterns:
            patterns.append(entry)

