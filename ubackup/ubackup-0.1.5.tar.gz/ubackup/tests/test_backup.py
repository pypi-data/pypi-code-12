import mock
import os
from ubackup.tests import TestCase
from ubackup.backup.base import Backup
from ubackup.backup.path import PathBackup
from ubackup.backup.mysql import MysqlBackup
from ubackup.utils import md5_stream
from ubackup.utils import stream_shell


class BucketTest(TestCase):

    def test_backup_base(self):
        backup = Backup()
        self.assertRaises(NotImplementedError, lambda: backup.TYPE)
        self.assertRaises(NotImplementedError, lambda: backup.stream)
        self.assertRaises(NotImplementedError, lambda: backup.data)
        self.assertRaises(NotImplementedError, lambda: backup.unique_name)
        self.assertRaises(NotImplementedError, lambda: backup.create())
        self.assertRaises(NotImplementedError, lambda: backup.checksum())
        self.assertRaises(NotImplementedError, lambda: backup.restore_command('foo'))

    def test_backup_path(self):
        with open(os.path.join(self.tmp_dir, 'foo'), 'w') as fp:
            fp.write('bar')

        backup = PathBackup(self.tmp_dir)

        # Checksum
        self.assertEqual(
            backup.checksum(),
            md5_stream(stream_shell(
                cmd='tar -cp .',
                cwd=self.tmp_dir)))

        # Create
        stream = backup.create()
        tmp_path = self.tmp_path()
        with open(tmp_path, 'w') as fp:
            fp.write(stream.read())

        backup.data
        backup.unique_name

        with open(tmp_path, 'r') as fp:
            backup.restore(fp)

    @mock.patch('ubackup.backup.mysql.MysqlBackup.restore_command')
    def test_backup_mysql_create(self, mock_restore_command):
        backup = MysqlBackup([])

        # Checksum
        md5_processed = md5_stream(backup.stream)
        md5_by_create = backup.checksum()
        self.assertEqual(md5_processed, md5_by_create)

        # Dump
        backup.databases = []
        backup.stream
        backup.databases = ['foo']
        backup.stream

        # Create
        stream = backup.create()
        tmp_path = self.tmp_path()
        with open(tmp_path, 'w') as fp:
            fp.write(stream.read())

        backup.data
        backup.unique_name

        with open(tmp_path, 'r') as fp:
            backup.restore(fp)

        self.assertTrue(mock_restore_command.called)
