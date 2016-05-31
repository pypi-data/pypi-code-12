from __future__ import absolute_import

from .base import Backup
from ubackup.utils import stream_shell
from subprocess import check_call


class PostgresqlBackup(Backup):
    TYPE = "postgresql"

    def __init__(self, databases):
        self.databases = databases

    @property
    def data(self):
        return {
            'databases': self.databases
        }

    @property
    def unique_name(self):
        return "postgresql-*"

    @property
    def stream(self):
        cmd = 'pg_dumpall'

        # Speed up mysql restore by setting some flags
        cmd = 'sudo -u postgres psql -c "select pg_start_backup(\'ubackup\', true);" '
        '&& %s && sudo -u postgres psql -c "select pg_stop_backup();"' % cmd

        return stream_shell(cmd)

    def restore_command(self, stream):
        check_call(
            ['psql -U postgres'],
            stdin=stream,
            shell=True)
