'''
tempfile does not seem to support `tempdir` correctly on all platforms,
so we add an override variable that we always support.

If the environment variable BAIJI_TMP is set, baiji will always write
its temporary download files there.
'''
from __future__ import absolute_import
import os
from baiji.util.shutillib import mkdir_p

def _override_tmp(fn, args, kwargs):
    if 'dir' not in kwargs:
        kwargs['dir'] = os.environ.get('BAIJI_TMP', None)
        if kwargs['dir'] is not None:
            mkdir_p(kwargs['dir'])
    return fn(*args, **kwargs)


def TemporaryFile(*args, **kwargs):
    from tempfile import TemporaryFile as _TemporaryFile
    return _override_tmp(_TemporaryFile, args, kwargs)

def NamedTemporaryFile(*args, **kwargs):
    from tempfile import NamedTemporaryFile as _NamedTemporaryFile
    return _override_tmp(_NamedTemporaryFile, args, kwargs)

def mkstemp(*args, **kwargs):
    from tempfile import mkstemp as _mkstemp
    return _override_tmp(_mkstemp, args, kwargs)

def mkdtemp(*args, **kwargs):
    from tempfile import mkdtemp as _mkdtemp
    return _override_tmp(_mkdtemp, args, kwargs)
