#!/usr/bin/env python
import unittest
import mock
from doormouse import cli


class TestCommandLineArgs(unittest.TestCase):
    """Tests the parsing of command line arguments."""
    def setUp(self):
        self.parser = cli.create_parser()

    @mock.patch.object(cli.argparse.ArgumentParser, "_print_message", mock.Mock())
    def test_empty(self):
        """Tests empty arguments."""
        with self.assertRaises(SystemExit) as exc:
            self.parser.parse_args([])
        self.assertNotEqual(0, exc.exception.code)

    def test_initialize(self):
        """Tests initialize command line parsing."""
        # empty
        args = self.parser.parse_args(["initialize"])
        self.assertEqual(args.command, "initialize")

    def test_list(self):
        """Tests the list command line parsing."""
        # empty
        args = self.parser.parse_args(["list"])
        self.assertEqual(args.command, "list")
        self.assertIsNone(args.issuer_nickname)

        # with ca
        args = self.parser.parse_args(["list", "foo"])
        self.assertEqual(args.command, "list")
        self.assertEqual(args.issuer_nickname, "foo")

    @mock.patch.object(cli.argparse.ArgumentParser, "_print_message", mock.Mock())
    def test_create(self):
        """Test the create command line parsing."""
        # empty
        with self.assertRaises(SystemExit) as exc:
            self.parser.parse_args(["create"])
        self.assertNotEqual(0, exc.exception.code)

        # without a common name
        with self.assertRaises(SystemExit) as exc:
            self.parser.parse_args(["create", "foo_ca"])
        self.assertNotEqual(0, exc.exception.code)

        # without alt names
        args = self.parser.parse_args(["create", "foo", "bar"])
        self.assertEqual(args.command, "create")
        self.assertEqual(args.cert_nickname, "foo")
        self.assertEqual(args.cn, "bar")
        self.assertFalse(args.alt)

        # with alt names
        args = self.parser.parse_args(["create", "foo", "bar", "a1", "a2", "a3"])
        self.assertEqual(args.command, "create")
        self.assertEqual(args.cert_nickname, "foo")
        self.assertEqual(args.cn, "bar")
        self.assertEqual(args.alt, ["a1", "a2", "a3"])

    @mock.patch.object(cli.argparse.ArgumentParser, "_print_message", mock.Mock())
    def test_sign(self):
        """Test the sign command line parsing."""
        # empty
        with self.assertRaises(SystemExit) as exc:
            self.parser.parse_args(["sign"])
        self.assertNotEqual(0, exc.exception.code)

        # without csr filename
        with self.assertRaises(SystemExit) as exc:
            self.parser.parse_args(["sign", "foo_ca"])
        self.assertNotEqual(0, exc.exception.code)

        # with everything needed
        args = self.parser.parse_args(["sign", "foo", "bar"])
        self.assertEqual(args.command, "sign")
        self.assertEqual(args.cert_nickname, "foo")
        self.assertEqual(args.request_filename, "bar")

    @mock.patch.object(cli.argparse.ArgumentParser, "_print_message", mock.Mock())
    def test_import(self):
        """Test the track command line parsing."""
        # empty
        with self.assertRaises(SystemExit) as exc:
            self.parser.parse_args(["import"])
        self.assertNotEqual(0, exc.exception.code)

        # with the cert filename
        args = self.parser.parse_args(["import", "foo"])
        self.assertEqual(args.command, "import")
        self.assertEqual(args.certfile, "foo")

    @mock.patch.object(cli.argparse.ArgumentParser, "_print_message", mock.Mock())
    def test_forget(self):
        """Test the forget command line parsing."""
        # empty
        with self.assertRaises(SystemExit) as exc:
            self.parser.parse_args(["forget"])
        self.assertNotEqual(0, exc.exception.code)

        # with the serial number
        args = self.parser.parse_args(["forget", "foo"])
        self.assertEqual(args.command, "forget")
        self.assertEqual(args.serial, "foo")

    @mock.patch.object(cli.argparse.ArgumentParser, "_print_message", mock.Mock())
    def test_warn(self):
        """Test the warn command line parsing."""
        # empty
        args = self.parser.parse_args(["warn"])
        self.assertEqual(args.command, "warn")
        self.assertEqual(args.days, 30)

        # with days
        args = self.parser.parse_args(["warn"])
        self.assertEqual(args.command, "warn")
        self.assertEqual(args.days, 30)

        args = self.parser.parse_args(["warn", "43"])
        self.assertEqual(args.command, "warn")
        self.assertEqual(args.days, 43)

        with self.assertRaises(SystemExit) as exc:
            self.parser.parse_args(["warn", "a"])
        self.assertNotEqual(0, exc.exception.code)

    @mock.patch.object(cli.argparse.ArgumentParser, "_print_message", mock.Mock())
    def test_revoke(self):
        """Tests the revoke command line parsing."""
        # empty
        with self.assertRaises(SystemExit) as exc:
            self.parser.parse_args(["revoke"])
        self.assertNotEqual(0, exc.exception.code)

        # list without ca
        args = self.parser.parse_args(["revoke", "list"])
        self.assertEqual(args.command, "revoke")
        self.assertEqual(args.subcommand, "list")
        self.assertIsNone(args.issuer_nickname)

        # list with ca
        args = self.parser.parse_args(["revoke", "list", "foo"])
        self.assertEqual(args.command, "revoke")
        self.assertEqual(args.subcommand, "list")
        self.assertEqual(args.issuer_nickname, "foo")

        # refresh without ca
        args = self.parser.parse_args(["revoke", "refresh"])
        self.assertEqual(args.command, "revoke")
        self.assertEqual(args.subcommand, "refresh")
        self.assertIsNone(args.issuer_nickname)

        # refresh with ca
        args = self.parser.parse_args(["revoke", "refresh", "foo"])
        self.assertEqual(args.command, "revoke")
        self.assertEqual(args.subcommand, "refresh")
        self.assertEqual(args.issuer_nickname, "foo")

        # certificate without serial
        with self.assertRaises(SystemExit) as exc:
            self.parser.parse_args(["revoke", "certificate"])
        self.assertNotEqual(0, exc.exception.code)

        # certificate with serial
        args = self.parser.parse_args(["revoke", "certificate", "foo"])
        self.assertEqual(args.command, "revoke")
        self.assertEqual(args.subcommand, "certificate")
        self.assertEqual(args.serial, "foo")
