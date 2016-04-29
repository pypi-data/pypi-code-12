from pathlib import Path, PurePath, _Flavour
import posixpath
from urllib.parse import quote_from_bytes

from qrc_pathlib import QtCore


class _QrcFlavour(_Flavour):
    sep = '/'
    altsep = ''
    has_drv = False
    pathmod = posixpath

    is_supported = True

    def splitroot(self, part, sep=sep):
        if part and part[0] == ':':
            if len(part) > 1 and part[1] == '/':
                return '', ':/', part[2:]
            else:
                return '', ':/', part[1:]
        else:
            return '', '', part

    def casefold(self, s):
        return s

    def casefold_parts(self, parts):
        return parts

    def resolve(self, path):
        if not QtCore.QFile(str(path)).exists():
            raise FileNotFoundError("No such file or directory: '{}'".format(str(path)))

        return QtCore.QFileInfo(str(path)).canonicalFilePath()

    def is_reserved(self, parts):
        return False

    def make_uri(self, path):
        bpath = bytes(path)

        if bpath.startswith(b':/'):
            bpath = bpath[2:]
        elif path.startswith(b':'):
            bpath = bpath[1:]

        return 'qrc:/' + quote_from_bytes(bpath)


class PureQrcPath(PurePath):
    _flavour = _QrcFlavour()
    __slots__ = ()

    def __bytes__(self):
        return self.__str__().encode('utf-8')
