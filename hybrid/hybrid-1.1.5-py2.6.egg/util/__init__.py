import re
import keyword
import os
import tempfile
import logging
import pkgutil
import sys
import zipimport

VALIDATE_REGEXP = re.compile('^[_a-zA-Z][0-9a-zA-Z_]*$')

def __get_filename_maxlen():
    if 'win' in sys.platform:
        return 255
    with tempfile.NamedTemporaryFile() as tmpfile:
        return os.pathconf(tmpfile.name, 'PC_NAME_MAX')
FILENAME_MAXLEN = __get_filename_maxlen()

def is_valid_name(name, maxlen=FILENAME_MAXLEN):
    if (not isinstance(name, str)) or \
        keyword.iskeyword(name) or \
        (not VALIDATE_REGEXP.match(name)) or \
        len(name) > maxlen:
        return False
    return True

def makedirs(d):
    d = os.path.abspath(d)
    if os.path.exists(d):
        return "'%s' already exists" % d
    try:
        os.makedirs(d)
    except OSError as e:
        return str(e)

COLOR = {
    "red": "\033[31m",
    "green": "\033[32m",
}

def find_modules(*a, **kw):
    hookfunc = kw.pop('hookfunc', lambda *a, **kw: True)
    for module_loader, name, ispkg in pkgutil.iter_modules(*a, **kw):
        if name in sys.modules:
            yield sys.modules[name]
            continue
        if not hookfunc(name):
            continue
        try:
            if isinstance(module_loader, pkgutil.ImpImporter):
                yield module_loader.find_module(name).load_module(name)
            elif isinstance(module_loader, zipimport.zipimporter):
                yield module_loader.load_module(name)
            logging.debug("succeed to import module:%s", name)
        except Exception as exc:
            logging.warn("failed to import module:%s, because:%s",
                    name, str(exc))

def imports(module):
    if os.sep in module:
        _name = os.path.basename(module)
        _path = [os.path.dirname(module)]
    else:
        _name = module
        _path = None
    try:
        return next(find_modules(_path,
                hookfunc=lambda name: name==_name))
    except StopIteration:
        pass

def ignore_exceptions(*exc):
    def _inner(f):
        def _innest(*a, **kw):
            try:
                return f(*a, **kw)
            except tuple([_ for _ in exc if
                 issubclass(_, Exception)]) as e:
                return e
        return _innest
    return _inner

