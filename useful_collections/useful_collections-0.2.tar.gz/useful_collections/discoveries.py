import sys
from types import ModuleType

class DiscoverySubModules(dict):
    def __init__(self, caller_mod):
        self.caller_mod = caller_mod
        for mod_name in dir(sys.modules[self.caller_mod]):
            mod_fullname = self.caller_mod + '.' + mod_name
            if mod_fullname in sys.modules.keys():
                if isinstance(sys.modules[mod_fullname], ModuleType):
                    self[mod_name] = sys.modules[mod_fullname]

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            raise SubModuleNotFound(
                "module object '{}' has no sub module '{}'".format(
                    self.caller_mod, key))

    def __getattr__(self, attr):
        try:
            return dict.__getitem__(self, attr)
        except KeyError:
            raise SubModuleNotFound("module object '{0}' has no sub module " \
                "'{1}' or type object 'DiscoverySubModules' has attribute " \
                "'{1}'".format(self.caller_mod, attr))

# class DiscoverySubClass(dict):
#     def __init__(self, caller_mod):
#         self.caller_mod = caller_mod
#         for class_name in dir(sys.modules[self.caller_mod]):
#             class_fullname = self.caller_mod + '.' + class_name
#             if class_fullname in sys.modules.keys():
#                 if isinstance(sys.modules[class_fullname], type):
#                     self[class_name] = sys.modules[class_fullname]
#
#         for internal_obj in ['DiscoverySubClass']:
#             if self.get(internal_obj):
#                 self.pop(internal_obj)
#
#     def __getitem__(self, key):
#         try:
#             return dict.__getitem__(self, key)
#         except KeyError:
#             raise SubClassNotFound(
#                 "module object '{}' has no sub class '{}'".format(
#                     self.caller_mod, key))
#
#     def __getattr__(self, attr):
#         try:
#             return dict.__getitem__(self, attr)
#         except KeyError:
#             raise SubClassNotFound("module object '{0}' has no sub class " \
#                 "'{1}' or type object 'DiscoverySubClass' has attribute " \
#                 "'{1}'".format(self.caller_mod, attr))


# Exceptions
class SubModuleNotFound(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)

# class SubClassNotFound(Exception):
#     def __init__(self, msg=None):
#         Exception.__init__(self, msg)
