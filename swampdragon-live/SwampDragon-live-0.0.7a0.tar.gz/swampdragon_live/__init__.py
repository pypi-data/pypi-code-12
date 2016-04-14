# -*- coding: utf-8 -*-
"""
SwampDragon-live is an extension to Django and SwampDragon which adds
support for live updating Django template snippets on model changes.
"""

__version_info__ = {
    'major': 0,
    'minor': 0,
    'micro': 7,
    'releaselevel': 'alpha',
}

def get_version():
    """
    Return the formatted version information
    """
    vers = ["%(major)i.%(minor)i" % __version_info__, ]

    if __version_info__['micro']:
        vers.append(".%(micro)i" % __version_info__)
    if __version_info__['releaselevel'] != 'final':
        vers.append('%(releaselevel)s' % __version_info__)
    return ''.join(vers)

__version__ = get_version()
