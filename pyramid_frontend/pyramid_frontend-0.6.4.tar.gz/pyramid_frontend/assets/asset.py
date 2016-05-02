from __future__ import absolute_import, print_function, division

import logging

import os
import tempfile
import io

from contextlib import contextmanager
from hashlib import sha1

import six

log = logging.getLogger(__name__)


class Asset(object):
    """
    Generic superclass for other asset handler classes to inherit from.
    """

    def __init__(self, url_path):
        self.url_path = url_path

    def write(self, key, contents, entry_point, output_dir):
        """
        Write the compiled result for a particular entry point to the
        appropriate file and map file.

        The ``contents`` field should always be a unicode type (str on 3.x).
        """
        assert isinstance(contents, six.text_type)
        log.debug('Write - key: %r, entry_point: %r', key, entry_point)
        hash = sha1(contents.encode('utf-8')).hexdigest()

        name = os.path.basename(entry_point)
        file_name = u'{name}-{hash}.{ext}'.format(
            name=name, hash=hash, ext=self.extension)
        file_path = os.path.join(output_dir, file_name)

        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        log.debug('Writing to %s ...', file_path)
        with io.open(file_path, 'w', encoding='utf8') as f:
            f.write(contents)

        map_path = os.path.join(output_dir, key + '.map')
        log.debug('Writing map file to %s ...', map_path)
        with io.open(map_path, 'w') as f:
            f.write(file_name)

        return file_path

    def write_from_file(self, key, file_name, entry_point, output_dir):
        """
        Like ``write()``, but writes from a source file instead of a buffer
        variable.
        """
        with io.open(file_name, encoding='utf8') as f:
            contents = f.read()
        return self.write(key, contents, entry_point, output_dir)

    @contextmanager
    def tempfile(self, *args, **kwargs):
        """
        A context manager helper to generate a temporary file for quick use.
        """
        f = tempfile.NamedTemporaryFile()
        try:
            yield f, f.name
        finally:
            f.close()

    def tag(self, theme, url, production=True):
        if production:
            return self.tag_production(theme, url)
        else:
            return self.tag_development(theme, url)
