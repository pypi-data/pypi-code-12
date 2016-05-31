from __future__ import absolute_import

from .base import Backup
from ubackup.utils import stream_shell
from subprocess import check_call


class MysqlBackup(Backup):
    TYPE = "mysql"

    def __init__(self, databases):
        self.databases = databases

    @property
    def data(self):
        return {
            'databases': self.databases
        }

    @property
    def unique_name(self):
        return "mysql-" + "-".join(self.databases)

    @property
    def stream(self):
        cmd = 'mysqldump -uroot --skip-comments'

        if len(self.databases) == 0:
            cmd += ' --all-databases'
        else:
            cmd += ' --databases %s' % " ".join(self.databases)

        # Speed up mysql restore by setting some flags
        cmd = "echo \"SET autocommit=0;SET unique_checks=0;SET foreign_key_checks=0;\" && %s && echo \"COMMIT;\"" % cmd

        return stream_shell(cmd)

    def restore_command(self, stream):
        check_call(
            ['mysql -uroot'],
            stdin=stream,
            shell=True)
