
# TODO: figure out this
raise Exception("Deprecated?")

import urllib

import mako.filters


def u_path_escape(text):
    return urllib.parse.quote(text)


def install():

    mako.filters.DEFAULT_ESCAPES['u_path'] = 'filters.u_path_escape'
    mako.filters.u_path_escape = u_path_escape
