import sys


def _int_minor_version(version):
    return version[0] * 100 + version[1]


def _int_micro_version(version):
    return version[0] * 10000 + version[1] * 100 + version[2]


def _valid_comparison(c):
    try:
        is_str = isinstance(c, basestring)
    except NameError:
        is_str = isinstance(c, str)
    if not is_str:
        cls = c.__class__.__name__
        raise ValueError('comparison must be a string, but is {0}({1})'.format(
            cls, str(c)))
    if c not in ('==', '<', '<=', '>', '>=', '!='):
        raise ValueError('comparison is not valid: {0}'.format(c))


def compare_major_python(s, comp='==', sysv=sys.version_info):
    _valid_comparison(comp)
    s = int(s)
    e = '{sys} {comp} {s}'.format(sys=sysv[0], comp=comp, s=s)
    return eval(e)


def compare_minor_python(varr, comp='==', sysv=sys.version_info):
    vi = _int_minor_version(varr)
    svi = _int_minor_version(sysv)
    e = '{svi} {comp} {vi}'.format(svi=svi, comp=comp, vi=vi)
    return eval(e)


def compare_micro_python(varr, comp='==', sysv=sys.version_info):
    vi = _int_micro_version(varr)
    svi = _int_micro_version(sysv)
    e = '{svi} {comp} {vi}'.format(svi=svi, comp=comp, vi=vi)
    return eval(e)


def compare_python(s, comp='==', sysv=sys.version_info):
    _valid_comparison(comp)
    if isinstance(s, (int, float)):
        s = str(s)
    s = s.strip()
    if not s:
        raise ValueError('comparing empty python version')
    version = [int(x) for x in s.split('.')]
    if len(version) == 1:
        return compare_major_python(version[0], comp=comp, sysv=sysv)
    elif len(version) == 2:
        return compare_minor_python(version, comp=comp, sysv=sysv)
    elif len(version) >= 3:
        version = version[:3]
        return compare_micro_python(version, comp=comp, sysv=sysv)
    else:
        raise NotImplementedError('logic error in len(version) check')


class PythonVersion(object):

    def __init__(self, sysv=sys.version_info):
        self._sysv = sysv

    def __eq__(self, val):
        return compare_python(val, comp='==', sysv=self._sysv)

    def __lt__(self, val):
        return compare_python(val, comp='<', sysv=self._sysv)

    def __le__(self, val):
        return compare_python(val, comp='<=', sysv=self._sysv)

    def __gt__(self, val):
        return compare_python(val, comp='>', sysv=self._sysv)

    def __ge__(self, val):
        return compare_python(val, comp='>=', sysv=self._sysv)

    def __ne__(self, val):
        return compare_python(val, comp='!=', sysv=self._sysv)

    def __getitem__(self, i):
        return self._sysv[i]


PYTHON = PythonVersion()
