import click
from uuid import uuid4
from ubackup.tests import TestCase
from ubackup.cli.validators import directory
from ubackup.cli.validators import mysql_databases


class ValidatorsTest(TestCase):

    def test_directory_success(self):
        directory(None, 'path', self.tmp_dir)

    def test_directory_fail(self):
        self.assertRaises(click.BadParameter, directory, None, 'path', uuid4().hex)

    def test_mysql_databases_success(self):
        self.assertEqual(mysql_databases(None, 'databases', '*'), [])
        self.assertEqual(mysql_databases(None, 'databases', 'foo'), ['foo'])
        self.assertEqual(mysql_databases(None, 'databases', 'foo,bar'), ['foo', 'bar'])
        self.assertEqual(mysql_databases(None, 'databases', 'foo bar'), ['foo', 'bar'])
        self.assertEqual(mysql_databases(None, 'databases', 'foo/bar'), ['foo', 'bar'])

    def test_mysql_databases_fail(self):
        self.assertRaises(click.BadParameter, mysql_databases, None, 'databases', ',')
