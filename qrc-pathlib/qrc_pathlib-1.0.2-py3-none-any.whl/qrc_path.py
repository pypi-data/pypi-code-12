from io import BytesIO, StringIO
from pathlib import Path

from qrc_pathlib import QtCore
from qrc_pathlib.pure_qrc_path import PureQrcPath
from qrc_pathlib.qrc_glob import iglob


class QrcPath(Path, PureQrcPath):
    #{ Path

    @classmethod
    def cwd(cls):
        raise NotImplementedError("Qt Resource System does not support cwd")

    @classmethod
    def home(cls):
        raise NotImplementedError("Qt Resource System does not support home")

    def _init(self, template=None):
        self._stat = QtCore.QFileInfo(str(self))
        self._closed = False

    def samefile(self, other_path):
        return self.resolve() == other_path.resolve()

    def iterdir(self):
        iter = QtCore.QDirIterator(str(self), QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Dirs | QtCore.QDir.Files)
        while iter.hasNext():
            yield QrcPath(iter.next())

    def glob(self, pattern):
        for p in iglob(pattern, recursive=True):
            yield self.__class__(p)

    def rglob(self, pattern):
        yield from self.glob('**/' + pattern)

    def stat(self):
        raise NotImplementedError("Qt Resource System does not support stat")

    def owner(self):
        raise NotImplementedError("Qt Resource System does not support ownership")

    def group(self):
        raise NotImplementedError("Qt Resource System does not support ownership")

    def open(self, mode='r', buffering=-1, encoding=None, errors=None, newline=None):
        if self.is_dir():
            raise IsADirectoryError("Is a directory: '{}'".format(str(self)))

        if buffering not in (-1, 0):
            raise ValueError("buffering must be either -1 or 0")

        if newline not in (None, ''):
            raise ValueError("newline must be either None or ''")

        if 'b' in mode and 't' in mode:
            raise ValueError("can't have text and binary mode at once")

        allowed_mode = ['r', 'b', 't']

        for c in mode:
            if c not in allowed_mode:
                raise ValueError("invalid mode: '{}'".format(mode))
            else:
                allowed_mode.remove(c)

        opening_mode = QtCore.QIODevice.ReadOnly

        if buffering == 0:
            opening_mode |= QtCore.QIODevice.Unbuffered

        if newline is None:
            opening_mode |= QtCore.QIODevice.Text

        f = QtCore.QFile(str(self))
        if f.open(opening_mode):
            try:
                data = f.readAll().data()  # QRC resource are compressed, there is no point of trying to reuse RAM

                if 'b' in mode:
                    return BytesIO(data)
                else:
                    return StringIO(data.decode(encoding=encoding or 'utf-8', errors=errors or 'strict'))
            finally:
                f.close()
        else:
            raise FileNotFoundError("No such file or directory: '{}'".format(str(self)))

    def write_bytes(self, data):
        raise PermissionError("Qt Resource System is read-only")

    def write_text(self, data, encoding=None, errors=None):
        raise PermissionError("Qt Resource System is read-only")

    def touch(self, mode=0o666, exist_ok=True):
        raise PermissionError("Qt Resource System is read-only")

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        raise PermissionError("Qt Resource System is read-only")

    def chmod(self, mode):
        raise PermissionError("Qt Resource System is read-only")

    def lchmod(self, mode):
        return self.chmod(mode)

    def unlink(self):
        raise PermissionError("Qt Resource System is read-only")

    def rmdir(self):
        raise PermissionError("Qt Resource System is read-only")

    def lstat(self):
        return self.stat()

    def rename(self, target):
        raise PermissionError("Qt Resource System is read-only")

    def replace(self, target):
        raise PermissionError("Qt Resource System is read-only")

    def symlink_to(self, target, target_is_directory=False):
        raise PermissionError("Qt Resource System is read-only")

    def exists(self):
        return self._stat.exists()

    def is_dir(self):
        return self._stat.isDir()

    def is_file(self):
        return self._stat.isFile()

    def is_symlink(self):
        return False

    def is_block_device(self):
        return False

    def is_char_device(self):
        return False

    def is_fifo(self):
        return False

    def is_socket(self):
        return False

    def expanduser(self):
        raise NotImplementedError("Qt Resource System does not support home")

    #{ QRCPath

    def copy_to(self, target):
        """
        Copy file to a given path.

        @type other_path: Path
        """
        f = QtCore.QFile(str(self))

        if not f.open(QtCore.QIODevice.ReadOnly):
            raise FileNotFoundError("No such file or directory: '{}'".format(str(self)))
        else:
            try:
                if not f.copy(target.as_posix()):
                    raise IOError("unable top copy '{}' to '{}': {}".format(str(self), str(target), f.error()))
            finally:
                f.close()
    #}
