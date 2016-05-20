from contextlib import closing
try:
    from cStringIO import StringIO
except ImportError:  # flake8: noqa
    from StringIO import StringIO
import os.path as osp
import mimetypes


class iterator_to_file(object):
    """Incomplete implementation of a file-like object on top of
    an iterator.
    """
    def __init__(self, it):
        self._it = it
        self._buf = ''

    def __iter__(self):
        return self

    def close(self):
        pass

    def read(self, size=-1):
        if size >= 0:
            return self._read_n(size)
        else:
            with closing(StringIO()) as res:
                buf = self._read_n(4096)
                res.write(buf)
                while len(buf) == 4096:
                    buf = self._read_n(4096)
                    res.write(buf)
                return res.getvalue()

    def _read_n(self, size):
        while len(self._buf) < size:
            try:
                data = self.next()
            except StopIteration:
                if len(self._buf) == 0:
                    return ''
                else:
                    res = self._buf
                    self._buf = ''
                    return res
            self._buf += data
            if len(data) == 0:
                break
        if len(self._buf) > size:
            res = self._buf[:size]
            self._buf = self._buf[size:]
        else:
            len(self._buf)
            res = self._buf
            self._buf = ''
        return res

    def next(self):
        return self._it.next()


class FileProperties(object):
    TYPE_CHECK = {
        '3gp': 'video',
        'aaf': 'video',
        'aiff': 'sound',
        'ami': 'document',
        'ape': 'sound',
        'asc': 'document',
        'asf': 'video',
        'ast': 'sound',
        'au': 'sound',
        'avchd': 'video',
        'avi': 'video',
        'bmp': 'image',
        'bwf': 'sound',
        'cdda': 'sound',
        'csv': 'document',
        'doc': 'document',
        'docm': 'document',
        'docx': 'document',
        'dot': 'document',
        'dotx': 'document',
        'epub': 'document',
        'flac': 'sound',
        'flv': 'video',
        'gdoc': 'document',
        'gif': 'image',
        'gslides': 'slide',
        'jpeg': 'image',
        'jpg': 'image',
        'key': 'slide',
        'keynote': 'slide',
        'm4a': 'sound',
        'm4p': 'sound',
        'm4v': 'video',
        'mkv': 'video',
        'mng': 'video',
        'mov': 'video',
        'movie': 'video',
        'mp3': 'sound',
        'mp4': 'video',
        'mpe': 'video',
        'mpeg': 'video',
        'mpg': 'video',
        'nb': 'slide',
        'nbp': 'slide',
        'nsv': 'video',
        'odm': 'document',
        'odp': 'slide',
        'ods': 'document',
        'odt': 'document',
        'ott': 'document',
        'pages': 'document',
        'pdf': 'document',
        'pez': 'slide',
        'png': 'image',
        'pot': 'slide',
        'pps': 'slide',
        'ppt': 'slide',
        'pptx': 'slide',
        'rtf': 'document',
        'sdw': 'document',
        'shf': 'slide',
        'shn': 'sound',
        'show': 'slide',
        'shw': 'slide',
        'swf': 'video',
        'thmx': 'slide',
        'txt': 'document',
        'wav': 'sound',
        'wma': 'sound',
        'wmv': 'video',
        'wpd': 'document',
        'wps': 'document',
        'wpt': 'document',
        'wrd': 'document',
        'wri': 'document',
        'xls': 'document',
        'xlsx': 'document'
    }

    MIMETYPE_CHECK = {
        'image/png': 'image',
        'image/jpeg': 'image',
        'image/jpg': 'image',
        'image/gif': 'image',
        'application/pdf': 'document',
        'application/vnd.google-apps.document': 'document',
        'application/vnd.google-apps.spreadsheet': 'document',
        'application/vnd.google-apps.photo': 'image',
        'application/vnd.google-apps.drawing': 'image',
        'application/vnd.google-apps.presentation': 'slide',
        'application/vnd.google-apps.video': 'video'
    }

    @classmethod
    def file_type(cls, filename, mime_type=None):
        filetype = None
        if filename:
            _, extension = osp.splitext(filename)
            extension = extension[1:]
            filetype = cls.TYPE_CHECK.get(extension)
        if filetype is None:
            filetype = cls.MIMETYPE_CHECK.get(mime_type, 'other')
        return filetype


    @classmethod
    def mime_type(cls, filename):
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type

