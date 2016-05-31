import os
import mock
from ubackup.tests import TestCase
from ubackup.manager import Manager
from ubackup.backup.path import PathBackup
from ubackup.utils import stream_shell


class ManagerTest(TestCase):

    @mock.patch('ubackup.backup.mysql.MysqlBackup.restore')
    @mock.patch('ubackup.backup.path.PathBackup.restore')
    def test_manager(self, *args, **kwargs):
        with open(os.path.join(self.tmp_dir, 'foo'), 'w') as fp:
            fp.write('bar')

        bucket_file_exists = True

        class TestBucket(object):
            TYPE = "test"

            def push(self, *args, **kwargs):
                pass

            def pull(self, *args, **kwargs):
                return stream_shell(cmd="echo 'foo'")

            def exists(self, name):
                return bucket_file_exists

            def get_revisions(self, name):
                return []

        manager = Manager(TestBucket())

        # Push backup
        backup = PathBackup(self.tmp_dir)
        manager.push_backup(backup)

        # Already exists
        manager.push_backup(backup)

        # Get revisions
        self.assertEqual(len(manager.get_revisions(backup)), 0)

        # Restore backup
        manager.restore_backup(backup, {'id': 1})
        bucket_file_exists = False
        self.assertRaises(Manager.ManagerError, manager.restore_backup, backup, {'id': 1})
