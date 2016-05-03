#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import sys

class Conf():
    """The global configuration class"""

    @staticmethod
    def get_real_paths(paths, nestchar):
        return [ path.split(nestchar) + ['raw'] for path in paths ]

    ARGS = sys.argv[1:]
    IN = sys.stdin
    OUT = sys.stdout
    OUT_DEBUG = sys.stderr
    OUT_WARNING = sys.stderr

    FLOW_DEF_NESTCHAR = '.'
    FLOW_DEF_STR = [
                'vlan{}id'.format(FLOW_DEF_NESTCHAR),
                'ip{}src'.format(FLOW_DEF_NESTCHAR),
                'ip{}dst'.format(FLOW_DEF_NESTCHAR),
                'ipv6{}src'.format(FLOW_DEF_NESTCHAR),
                'ipv6{}dst'.format(FLOW_DEF_NESTCHAR),
                'udp{}stream'.format(FLOW_DEF_NESTCHAR),
                'tcp{}stream'.format(FLOW_DEF_NESTCHAR),
    ]
    FLOW_DEF = get_real_paths.__func__(FLOW_DEF_STR, FLOW_DEF_NESTCHAR)
    DATA_MAXLEN = 200
    DATA_TOO_LONG = 'Data too long'
    PDML_NESTCHAR = '.'
    FLOW_BUFFER_TIME = 180
    EXTRACT_SHOW = False
    STANDALONE = False
    XML_OUTPUT = False
    COMPRESS_DATA = False
    FRAMES_ARRAY = False
    DEBUG = False
    METADATA = False
    PARSE_SOURCE = sys.stdin

    @staticmethod
    def set(conf):
        """Applies a configuration to the global config object"""
        for name, value in conf.items():
            if value is not None:
                setattr(Conf, name.upper(), value)

    @staticmethod
    def get():
        """Gets the configuration as a dict"""
        return {attr: getattr(Conf, attr) for attr in dir(Conf()) if not callable(getattr(Conf, attr)) and not attr.startswith("__")}

