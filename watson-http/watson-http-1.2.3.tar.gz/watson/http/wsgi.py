# -*- coding: utf-8 -*-
import cgi
import collections
from io import BytesIO, BufferedReader
from watson.common.contextmanagers import suppress


__all__ = ['get_form_vars']


def read_binary(self):
    """Override for FieldStorage.read_binary method.

    Existing FieldStorage method raises a "TypeError: must be str, not bytes"
    when CONTENT_LENGTH is specified for a body that isn't key=value pairs.
    Decoding the data into the relevant encoding resolves the issue.
    """
    todo = self.length
    if todo >= 0:
        while todo > 0:
            data = self.fp.read(min(todo, self.bufsize))
            if not isinstance(data, bytes):
                raise ValueError("%s should return bytes, got %s"
                                 % (self.fp, type(data).__name__))
            self.bytes_read += len(data)
            if not data:
                self.done = -1
                break
            if not self.file:
                self._binary_file = isinstance(data, bytes)
                self.file = self.make_file()
            if not self._binary_file:
                data = data.decode(self.encoding)  # The fix
            self.file.write(data)
            todo = todo - len(data)


cgi.FieldStorage.read_binary = read_binary

WSGI_BODY = 'wsgi.body.original'


def copy_wsgi_input(environ):
    """Copies a wsgi.input key so that it is seekable.
    """
    if WSGI_BODY not in environ:
        content_length = environ.get('CONTENT_LENGTH', '')
        length = int(content_length) if content_length else 0
        body = environ['wsgi.input'].read(length)
        environ[WSGI_BODY] = body
        environ['wsgi.input'] = BufferedReader(BytesIO(body))


def get_form_vars(environ, dict_type):
    """Convert environ vars into GET/POST/FILES objects.

    Process all get and post vars from a <form> and return MultiDict of
    each.
    """
    if environ['REQUEST_METHOD'] == 'PUT' and not environ.get('CONTENT_TYPE'):
        environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
    field_storage = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ,
                                     keep_blank_values=True)
    post_dict, files_dict = dict_type(), dict_type()
    with suppress(Exception):
        post_dict._mutable = True
        files_dict._mutable = True
    post, files = _process_field_storage(field_storage, post_dict, files_dict)
    with suppress(Exception):
        post.make_immutable()
        files.make_immutable()
    return post, files


File = collections.namedtuple(
    'File',
    'data filename name type type_options disposition disposition_options headers raw_field')


def _process_field_storage(fs, post, files):
    with suppress(Exception):
        for name in fs:
            field = fs[name] if isinstance(name, str) else name
            if isinstance(field, list):
                _process_field_storage(field, post, files)
            elif field.filename:
                # An uploaded file, create a new File tuple to resolve the
                # not indexable issue.
                files[field.name] = File(
                    field.file,
                    field.filename,
                    field.name,
                    field.type,
                    field.type_options,
                    field.disposition,
                    field.disposition_options,
                    field.headers,
                    field)
            else:
                post[field.name] = field.value
    return post, files
