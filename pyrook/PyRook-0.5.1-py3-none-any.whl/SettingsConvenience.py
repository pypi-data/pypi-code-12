

from .Importer.QtCore import *



# convenience methods to deal with inconsistent QSettings behaviour for bools
def settings_set_bool(key, value, settings=None):
    if not settings:
        settings = QSettings()
    settings.setValue(key, "true" if value else "false")

def settings_get_bool(key, default=False, settings=None):
    if not settings:
        settings = QSettings()
    value = settings.value(key, "none")
    if value == "none":
        return default
    elif value in ("false", False):
        return False
    elif value in ("true", True):
        return True
    return default
