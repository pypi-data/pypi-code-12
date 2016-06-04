'''
loggylog.logger

The main implementation of Logger is here.
'''
import os
import sys
from datetime import datetime

__all__ = ['Logger']

LEVELS = ['debug', 'info', 'warning', 'critical', 'error']
SPECIAL_FILES = ['<stdout>', '<stderr>']


class Logger(object):

    def __init__(self, fmt='{ts} [{level}] {msg}', **kwargs):
        self._logger_kwargs = kwargs
        self._level_map = {}
        self._fmt = fmt

    def _format(self, level, msg):
        ts = datetime.now().isoformat()
        return self._fmt.format(ts=ts, level=LEVELS[level].upper(), msg=msg)

    def _split_levels(self, level):
        if isinstance(level, (list, tuple, set)):
            return [
                x.strip().lower()
                for x in level
                if x.strip()
            ]
        if isinstance(level, str):
            if ',' in level:
                return [
                    x.strip().lower()
                    for x in level.split(',')
                    if x.strip()
                ]
            i = LEVELS.index(level.lower().strip())
            return LEVELS[i:]

    def _do_sudo(self, path):
        if path.lower() in SPECIAL_FILES:
            return
        if os.path.exists(path):
            if os.access(path, os.W_OK):
                return
            else:
                # chown path
                pass
        else:
            dname = os.path.dirname(path)
            if os.access(dname, os.W_OK):
                return
            else:
                # sudo touch
                # chown file
                pass

    def _convert_level(self, level):
        if level.lower() not in LEVELS:
            raise ValueError('{} is not a valid logging level'.format(level))
        return LEVELS.index(level.lower())

    def _setup_kwargs(self, kwargs):
        if self._logger_kwargs:
            fmt_kwargs = self._logger_kwargs.copy()
            fmt_kwargs.update(kwargs)
            return fmt_kwargs
        return kwargs

    def add_log(self, path, level='debug', sudo=False):
        path = path.strip()
        dname = os.path.dirname(path)
        if path.lower() in SPECIAL_FILES:
            path = path.lower()
        elif not os.path.exists(dname):
            raise IOError('{} does not exists, can\'t write to {}'.format(
                dname, path))
        levels = self._split_levels(level)
        for lvl in levels:
            i = self._convert_level(lvl)
            if i not in self._level_map:
                self._level_map[i] = []
            self._level_map[i] += [path]
        if sudo:
            self._do_sudo(path)

    def write(self, level, msg):
        paths = self._level_map.get(level)
        if not paths:
            return
        msg = self._format(level, msg)
        for path in paths:
            if path in SPECIAL_FILES:
                if path == '<stdout>':
                    print(msg)
                else:
                    print(msg, file=sys.stderr)
                continue
            with open(path, 'a') as f:
                f.write(msg + '\n')

    def debug(self, msg, *args, **kwargs):
        kwargs = self._setup_kwargs(kwargs)
        if args or kwargs:
            msg = msg.format(*args, **kwargs)
        self.write(0, msg)

    def info(self, msg, *args, **kwargs):
        kwargs = self._setup_kwargs(kwargs)
        if args or kwargs:
            msg = msg.format(*args, **kwargs)
        self.write(1, msg)

    def warning(self, msg, *args, **kwargs):
        kwargs = self._setup_kwargs(kwargs)
        if args or kwargs:
            msg = msg.format(*args, **kwargs)
        self.write(2, msg)

    def critical(self, msg, *args, **kwargs):
        kwargs = self._setup_kwargs(kwargs)
        if args or kwargs:
            msg = msg.format(*args, **kwargs)
        self.write(3, msg)

    def error(self, msg, *args, **kwargs):
        kwargs = self._setup_kwargs(kwargs)
        if args or kwargs:
            msg = msg.format(*args, **kwargs)
        self.write(4, msg)
