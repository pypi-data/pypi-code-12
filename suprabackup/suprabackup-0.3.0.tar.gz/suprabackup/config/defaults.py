"""
This module stores default configuration options for each role

"""

__defaults__ = {
    'send': {},
    'receive': {
        'base_path': '/tmp',
        'file_prefix': 'xtrabackup',
        'read_size': 32768,
        'database': {},
    },
    'shell': {},
    'verify': {},
    'purge': {},
}


def load_defaults(role):
    """
    This helper returns the defaults config options for `role`

    """
    return __defaults__.get(role, {})
