from woodstove import log
from woodstove import conf


PLUGIN_LIST = conf.get('woodstove', 'plugin_list', [])


__plugins__ = []


def load_plugin(name):
    try:
        __plugins__.append(__import__(name))
    except BaseException:
        log.get_logger(__name__).error("Error importing plugin `%s`", name)
        log.log_traceback(__name__)
    log.get_logger(__name__).info("Loaded plugin: %s", name)


def load_plugins():
    for name in PLUGIN_LIST:
        load_plugin(name)
