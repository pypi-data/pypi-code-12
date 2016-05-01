import os
import collections
import click

from morenines.util import get_hash, timestamp_now


class Index(object):
    reader_version = 1

    @classmethod
    def _check_version(cls, headers):
        try:
            version = headers['version']
        except KeyError as e:
            missing_key = e.args[0]
            raise Exception("Invalid file format: missing required header '{}'".format(missing_key))

        if version != str(cls.reader_version):
            raise Exception("Unsupported file format version: file is {}, parser is {}".format(version, cls.reader_version))

    def __init__(self, path_prefix):
        self.path_prefix = path_prefix
        self.files = collections.OrderedDict()

    def read(self, path):
        with click.open_file(path, 'r') as stream:
            headers = parse_headers(stream)

            self._check_version(headers)

            self.date = headers['date']

            if 'parent' in headers:
                self.parent = headers['parent']

            self.files = parse_files(stream)

    def add(self, paths):
        for path in paths:
            # To hash the file, we need its absolute path
            abs_path = os.path.join(self.path_prefix, path)

            # We store the relative path in the index, not the absolute
            self.files[path] = get_hash(abs_path)

    def remove(self, paths):
        for path in paths:
            del self.files[path]

    def write(self, stream):
        headers = [
            ('version', self.reader_version),
            ('date', timestamp_now()),
        ]

        # If we have a parent property, add it to the headers to write
        # Note: Using try/except instead of hasattr because the latter can hide
        # other exceptions in Python 2.
        try:
            headers.append(('parent', self.parent))
        except AttributeError:
            # If there's no parent property, this is the first index
            pass

        for key, value in headers:
            stream.write("{}: {}\n".format(key, value))

        # Separate the headers from the files list with a blank line
        stream.write("\n")

        # Write files and hashes -- but sort the paths before writing
        for path in sorted(self.files):
            stream.write("{} {}\n".format(self.files[path], path))


##############################
# Index file parsing functions
##############################

def split_lines(lines, delim, num_fields):
    """Split each element in the sequence 'lines' into its component fields."""
    for line in lines:
        if line == '\n':
            return

        yield [field.strip() for field in line.split(delim, num_fields - 1)]

def parse_headers(file_):
    """Parse header lines of the form 'key: value'"""
    return {key: value for key, value in split_lines(file_, ':', 2)}

def parse_files(file_):
    """Parse file lines of the form 'HASHVALUE /path/to/file"""
    return {path:hash_ for hash_, path in split_lines(file_, ' ', 2)}
