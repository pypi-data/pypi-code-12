import os
import subprocess
import sys
from types import ModuleType

import nose

if sys.version_info < (3, ):
    string_types = (basestring, )
else:
    string_types = (str, )


__all__ = ['run', 'get_path', 'get_argv']


def run(package, open_html=False, **kwargs):
    if open_html and 'html' not in kwargs:
        kwargs['html'] = True

    path = get_path(package)
    argv = get_argv(path, **kwargs)
    nose.run(argv=argv)

    if open_html:
        subprocess.call(['open', './cover/index.html'],
                        cwd=path)


def get_path(package):
    if isinstance(package, string_types):
        path = __import__(package).__file__
    elif isinstance(package, ModuleType):
        path = package.__file__
    else:
        msg = ('Expected ModuleType or String.' +
               ' got {}'.format(type(package)))
        raise TypeError(msg)

    return os.path.dirname(path)


def get_argv(path=None, **kwargs):
    argv = [sys.argv[0]]
    if path is not None:
        argv += [path]

    if 'cover' in kwargs and kwargs['cover']:
        argv += ['--with-coverage',
                 '--cover-erase',
                 '--cover-package={}'.format(path)]

    if 'html' in kwargs and kwargs['html']:
        if 'cover' not in kwargs:
            kwargs['cover'] = True
            return get_argv(path, **kwargs)
        argv += ['--cover-html',
                 '--cover-html-dir={}/cover'.format(path)]

    if 'xml' in kwargs and kwargs['xml']:
        if 'cover' not in kwargs:
            kwargs['cover'] = True
            return get_argv(path, **kwargs)
        argv += ['--cover-xml',
                 '--cover-xml-file={}'.format(path)]

    return argv
