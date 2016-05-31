from __future__ import absolute_import

from .base import Backup
from ubackup.utils import stream_shell
from subprocess import check_call

import logging
logger = logging.getLogger(__name__)


class ZfsBackup(Backup):
    TYPE = "zfs"

    def __init__(self, filesystem, precmd=None, postcmd=None):
        self.filesystem = filesystem
        self.precmd = precmd
        self.postcmd = postcmd

    @property
    def data(self):
        return {
            'filesystem': self.filesystem
        }

    @property
    def unique_name(self):
        return "filesystem-" + self.filesystem

    @property
    def stream(self):
        return stream_shell(
            cmd='tar -cp .',
            cwd=self.path)

    def restore_command(self, stream):
        check_call(
            ['tar -xp'],
            stdin=stream,
            cwd=self.path,
            shell=True)
