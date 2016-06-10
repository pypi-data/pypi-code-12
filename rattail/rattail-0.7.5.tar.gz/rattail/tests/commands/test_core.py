# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import csv
import datetime
import argparse
from unittest import TestCase
from cStringIO import StringIO

# from sqlalchemy import func
from mock import patch, Mock
from fixture import TempIO

from rattail.commands import core
from rattail.db import Session, model
from rattail.db.auth import authenticate_user
from rattail.tests import DataTestCase


class TestArgumentParser(TestCase):

    def test_parse_args_preserves_extra_argv(self):
        parser = core.ArgumentParser()
        parser.add_argument('--some-optional-arg')
        parser.add_argument('some_required_arg')
        args = parser.parse_args([
                '--some-optional-arg', 'optional-value', 'required-value',
                'some', 'extra', 'args'])
        self.assertEqual(args.some_required_arg, 'required-value')
        self.assertEqual(args.some_optional_arg, 'optional-value')
        self.assertEqual(args.argv, ['some', 'extra', 'args'])


class TestDateArgument(TestCase):

    def test_valid_date_string_returns_date_object(self):
        date = core.date_argument('2014-01-01')
        self.assertEqual(date, datetime.date(2014, 1, 1))

    def test_invalid_date_string_raises_error(self):
        self.assertRaises(argparse.ArgumentTypeError, core.date_argument, 'invalid-date')


class TestCommand(TestCase):

    def test_initial_subcommands_are_sane(self):
        command = core.Command()
        self.assertTrue('filemon' in command.subcommands)

    def test_unicode(self):
        command = core.Command()
        command.name = 'some-app'
        self.assertEqual(unicode(command), u'some-app')
        
    def test_iter_subcommands_includes_expected_item(self):
        command = core.Command()
        found = False
        for subcommand in command.iter_subcommands():
            if subcommand.name == 'filemon':
                found = True
                break
        self.assertTrue(found)

    def test_print_help(self):
        command = core.Command()
        stdout = StringIO()
        command.stdout = stdout
        command.print_help()
        output = stdout.getvalue()
        stdout.close()
        self.assertTrue('Usage:' in output)
        self.assertTrue('Options:' in output)

    def test_run_with_no_args_prints_help(self):
        command = core.Command()
        with patch.object(command, 'print_help') as print_help:
            command.run()
            print_help.assert_called_once_with()

    def test_run_with_single_help_arg_prints_help(self):
        command = core.Command()
        with patch.object(command, 'print_help') as print_help:
            command.run('help')
            print_help.assert_called_once_with()

    def test_run_with_help_and_unknown_subcommand_args_prints_help(self):
        command = core.Command()
        with patch.object(command, 'print_help') as print_help:
            command.run('help', 'invalid-subcommand-name')
            print_help.assert_called_once_with()

    def test_run_with_help_and_subcommand_args_prints_subcommand_help(self):
        command = core.Command()
        fake = command.subcommands['fake'] = Mock()
        command.run('help', 'fake')
        fake.return_value.parser.print_help.assert_called_once_with()

    def test_run_with_unknown_subcommand_arg_prints_help(self):
        command = core.Command()
        with patch.object(command, 'print_help') as print_help:
            command.run('invalid-command-name')
            print_help.assert_called_once_with()

    def test_stdout_may_be_redirected(self):
        class Fake(core.Subcommand):
            def run(self, args):
                self.stdout.write("standard output stuff")
                self.stdout.flush()
        command = core.Command()
        fake = command.subcommands['fake'] = Fake
        tmp = TempIO()
        config_path = tmp.putfile('test.ini', '')
        out_path = tmp.putfile('out.txt', '')
        command.run('fake', '--config', config_path, '--stdout', out_path)
        with open(out_path) as f:
            self.assertEqual(f.read(), "standard output stuff")

    def test_stderr_may_be_redirected(self):
        class Fake(core.Subcommand):
            def run(self, args):
                self.stderr.write("standard error stuff")
                self.stderr.flush()
        command = core.Command()
        fake = command.subcommands['fake'] = Fake
        tmp = TempIO()
        config_path = tmp.putfile('test.ini', '')
        err_path = tmp.putfile('err.txt', '')
        command.run('fake', '--config', config_path, '--stderr', err_path)
        with open(err_path) as f:
            self.assertEqual(f.read(), "standard error stuff")

    # # TODO: Figure out a better way to test this, or don't bother.
    # def test_noinit_flag_means_no_config(self):
    #     command = commands.Command()
    #     fake = command.subcommands['fake'] = Mock()
    #     command.run('fake', '--no-init')
    #     self.assertEqual(len(fake.return_value.config.files_requested), 0)


class TestSubcommand(TestCase):

    def test_repr(self):
        command = core.Command()
        subcommand = core.Subcommand(command)
        subcommand.name = 'fake-command'
        self.assertEqual(repr(subcommand), "Subcommand(name=u'fake-command')")

    def test_add_parser_args_does_nothing(self):
        command = core.Command()
        subcommand = core.Subcommand(command)
        # Not sure this is really the way to test this, but...
        self.assertEqual(len(subcommand.parser._action_groups[0]._actions), 1)
        subcommand.add_parser_args(subcommand.parser)
        self.assertEqual(len(subcommand.parser._action_groups[0]._actions), 1)

    def test_run_not_implemented(self):
        command = core.Command()
        subcommand = core.Subcommand(command)
        args = subcommand.parser.parse_args([])
        self.assertRaises(NotImplementedError, subcommand.run, args)


class TestAddUser(DataTestCase):
    
    def setUp(self):
        super(TestAddUser, self).setUp()
        self.tmp = TempIO()
        self.stdout_path = self.tmp.putfile('stdout.txt', '')
        self.stderr_path = self.tmp.putfile('stderr.txt', '')

    def test_no_user_created_if_username_already_exists(self):
        self.session.add(model.User(username='fred'))
        self.session.commit()
        self.assertEqual(self.session.query(model.User).count(), 1)
        core.main('adduser', '--no-init', '--stderr', self.stderr_path, 'fred')
        with open(self.stderr_path) as f:
            self.assertEqual(f.read(), "User 'fred' already exists.\n")
        self.assertEqual(self.session.query(model.User).count(), 1)

    # TODO: this breaks when postgres used for test db backend?
    # def test_no_user_created_if_password_prompt_is_canceled(self):
    #     self.assertEqual(self.session.query(model.User).count(), 0)
    #     with patch('rattail.commands.core.getpass') as getpass:
    #         getpass.side_effect = KeyboardInterrupt
    #         core.main('adduser', '--no-init', '--stderr', self.stderr_path, 'fred')
    #     with open(self.stderr_path) as f:
    #         self.assertEqual(f.read(), "\nOperation was canceled.\n")
    #     self.assertEqual(self.session.query(model.User).count(), 0)

    def test_normal_user_created_with_correct_password_but_no_admin_role(self):
        self.assertEqual(self.session.query(model.User).count(), 0)
        with patch('rattail.commands.core.getpass') as getpass:
            getpass.return_value = 'fredpass'
            core.main('adduser', '--no-init', '--stdout', self.stdout_path, 'fred')
        with open(self.stdout_path) as f:
            self.assertEqual(f.read(), "Created user: fred\n")
        fred = self.session.query(model.User).one()
        self.assertEqual(fred.username, 'fred')
        self.assertEqual(len(fred.roles), 0)
        user = authenticate_user(self.session, 'fred', 'fredpass')
        self.assertTrue(user is fred)

    def test_admin_user_created_with_administrator_role(self):
        self.assertEqual(self.session.query(model.User).count(), 0)
        with patch('rattail.commands.core.getpass') as getpass:
            getpass.return_value = 'fredpass'
            core.main('adduser', '--no-init', '--stdout', self.stdout_path, 'fred', '--administrator')
        fred = self.session.query(model.User).one()
        self.assertEqual(len(fred.roles), 1)
        self.assertEqual(fred.roles[0].name, 'Administrator')


class TestDump(DataTestCase):

    def setUp(self):
        super(TestDump, self).setUp()
        self.session.add(model.Product(upc='074305001321'))
        self.session.add(model.Product(upc='074305001161'))
        self.session.commit()

    def test_unknown_model_cannot_be_dumped(self):
        tmp = TempIO()
        stderr_path = tmp.putfile('stderr.txt', '')
        self.assertRaises(SystemExit, core.main, '--no-init', '--stderr', stderr_path, 'dump', 'NoSuchModel')
        with open(stderr_path) as f:
            self.assertEqual(f.read(), "Unknown model: NoSuchModel\n")

    def test_dump_goes_to_stdout_by_default(self):
        tmp = TempIO()
        stdout_path = tmp.putfile('stdout.txt', '')
        core.main('--no-init', '--stdout', stdout_path, 'dump', 'Product')
        with open(stdout_path, 'rb') as csv_file:
            reader = csv.DictReader(csv_file)
            upcs = [row['upc'] for row in reader]
        self.assertEqual(len(upcs), 2)
        self.assertTrue('00074305001321' in upcs)
        self.assertTrue('00074305001161' in upcs)

    def test_dump_goes_to_file_if_so_invoked(self):
        tmp = TempIO()
        output_path = tmp.putfile('output.txt', '')
        core.main('--no-init', 'dump', 'Product', '--output', output_path)
        with open(output_path, 'rb') as csv_file:
            reader = csv.DictReader(csv_file)
            upcs = [row['upc'] for row in reader]
        self.assertEqual(len(upcs), 2)
        self.assertTrue('00074305001321' in upcs)
        self.assertTrue('00074305001161' in upcs)


# TODO: more broken tests..ugh.  these aren't very good or else i might bother
# fixing them...
# class TestFileMonitor(TestCase):

#     @patch('rattail.filemon.linux.start_daemon')
#     def test_start_daemon_with_default_args(self, start_daemon):
#         commands.main('filemon', '--no-init', 'start')
#         start_daemon.assert_called_once_with(None, None, True)

#     @patch('rattail.filemon.linux.start_daemon')
#     def test_start_daemon_with_explicit_args(self, start_daemon):
#         tmp = TempIO()
#         pid_path = tmp.putfile('test.pid', '')
#         commands.main('filemon', '--no-init', '--pidfile', pid_path, '--do-not-daemonize', 'start')
#         start_daemon.assert_called_once_with(None, pid_path, False)

#     @patch('rattail.filemon.linux.stop_daemon')
#     def test_stop_daemon_with_default_args(self, stop_daemon):
#         commands.main('filemon', '--no-init', 'stop')
#         stop_daemon.assert_called_once_with(None, None)

#     @patch('rattail.filemon.linux.stop_daemon')
#     def test_stop_daemon_with_explicit_args(self, stop_daemon):
#         tmp = TempIO()
#         pid_path = tmp.putfile('test.pid', '')
#         commands.main('filemon', '--no-init', '--pidfile', pid_path, 'stop')
#         stop_daemon.assert_called_once_with(None, pid_path)

#     @patch('rattail.commands.sys')
#     def test_unknown_platform_not_supported(self, sys):
#         tmp = TempIO()
#         stderr_path = tmp.putfile('stderr.txt', '')
#         sys.platform = 'bogus'
#         commands.main('--no-init', '--stderr', stderr_path, 'filemon', 'start')
#         sys.exit.assert_called_once_with(1)
#         with open(stderr_path) as f:
#             self.assertEqual(f.read(), "File monitor is not supported on platform: bogus\n")


# # TODO: The purge-batches command tests don't work yet; the db.batches.util
# # tests need to be figured out first...
# class TestPurgeBatches(DataTestCase):

#     def setUp(self):
#         super(TestPurgeBatches, self).setUp()
#         self.session.add(model.Batch(purge=datetime.date(2014, 1, 1)))
#         self.session.add(model.Batch(purge=datetime.date(2014, 2, 1)))
#         self.session.add(model.Batch(purge=datetime.date(2014, 3, 1)))
#         self.session.commit()
#         self.tmp = TempIO()
#         self.stdout_path = self.tmp.putfile('stdout.txt', '')

#     def test_purging_honors_batch_purge_dates(self):
#         self.assertEqual(self.session.query(model.Batch).count(), 3)
#         commands.main('--no-init', '--stdout', self.stdout_path, 'purge-batches', '--date', '2014-01-15')
#         self.assertEqual(self.session.query(model.Batch).count(), 2)
#         self.assertEqual(self.session.query(func.min(model.Batch.purge)).scalar(), datetime.date(2014, 2, 1))
#         with open(self.stdout_path) as f:
#             self.assertTrue(f.read().endswith("\nPurged 1 normal and 0 orphaned batches.\n"))

#     def test_specifying_all_purges_everything(self):
#         self.assertEqual(self.session.query(model.Batch).count(), 3)
#         commands.main('--no-init', '--stdout', self.stdout_path, 'purge-batches', '--all')
#         self.assertEqual(self.session.query(model.Batch).count(), 0)
#         with open(self.stdout_path) as f:
#             self.assertTrue(f.read().endswith("\nPurged 3 normal and 0 orphaned batches.\n"))

#     def test_orphaned_tables_are_also_purged(self):
#         self.session.delete(self.session.query(model.Batch).first())
#         self.session.commit()
#         self.assertEqual(self.session.query(model.Batch).count(), 2)
#         commands.main('--no-init', '--stdout', self.stdout_path, 'purge-batches', '--date', '2013-12-31')
#         self.assertEqual(self.session.query(model.Batch).count(), 2)
#         with open(self.stdout_path) as f:
#             self.assertTrue(f.read().endswith("\nPurged 0 normal and 1 orphaned batches.\n"))
