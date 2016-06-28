# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from os.path import join, exists, getmtime

import mne

from .. import load


class Pipe(object):

    _path = ""

    def is_up_to_date(self, options):
        return True

    def load(self, options):
        "Make and load the file"
        raise NotImplementedError

    def mtime(self, options):
        "modification time of anythin influencing the output of load"
        return getmtime(self._path.format(options))


class EventPipe(Pipe):

    _path = join("{root}")

    def __init__(self, raw_src):
        self._raw_src = raw_src

    def load(self, options):
        path = self._path.format(options)
        if exists(path) and getmtime(path) > self._raw_src.mtime(options):
            return load.unpickle(path)
        raw = self._raw_src.load(options)


class EvokedPipe(Pipe):


class RawPipe(Pipe):

    _raw_path = join("{root}")
    _path = join("{root}")

    def __init__(self, config, raw_source):
        self._config = config
        self._raw_source = raw_source

    def is_up_to_date(self, options):
        if options['raw'] == 'raw':
            return self._raw_source.is_up_to_date(options)


    def load(self, options):
        if options['raw'] == 'raw':
            path = self._raw_path.format(options)
            if not exists(path):
                raise IOError("Input file does not exist: %s" % path)
            raw = mne.io.read_raw_fif(path)
        else:
            path = self._path.format(options)
            options_ = options.copy()
            options_['raw'] = 'raw'
            if not exists(path) or self.mtime(options_) > self.mtime(options):
                raw = self.load(options_)
                # ...
                raw.save(path)
            else:
                raw = mne.io.read_raw_fif(path)
        return raw

    def mtime(self, options):
        if options['raw'] == 'raw':
            return getmtime(self._raw_path.format(options))
        else:
            return getmtime(self._path.format(options))


class RawSource(Pipe):

    def is_up_to_date(self, options):
        path = format(self.)


