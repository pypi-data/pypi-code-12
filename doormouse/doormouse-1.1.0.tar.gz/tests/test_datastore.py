#!/usr/bin/env python
import os
import unittest
import mock
import sqlite3
import tempfile
import shutil
from doormouse import x509
from doormouse.datastore import DataStore, DataStoreError


class TestDatastore(unittest.TestCase):
    """Tests the datastore functionality."""
    def setUp(self):
        """Sets up each individual test by creating an empty database in memory."""
        self.datastore = DataStore("/dev/null", "")
        self.conn = sqlite3.connect(":memory:")
        DataStore._create_tables(self.conn)
        self.conn_mock = mock.Mock(return_value=self.conn)

    def tearDown(self):
        """Tears down each individual test by closing (deleting) the database."""
        self.conn.close()

    def assertEqualCert(self, issuer_nickname, profile_nickname, cert, cert_dict, status, cert_type):
        """Asserts that the certificate is equal to the cert_dict from datastore."""
        if not cert_dict:
            raise AssertionError("cert values not found")

        self.assertEqual(issuer_nickname, cert_dict["issuer_nickname"])
        self.assertEqual(profile_nickname, cert_dict["profile_nickname"])
        self.assertEqual(cert_type, cert_dict["cert_type"])
        self.assertEqual(status, cert_dict["status"])
        self.assertEqual("rsa", cert_dict["key_type"])
        self.assertEqual(2048, cert_dict["key_size"])
        self.assertEqual(cert.get_notBefore(), cert_dict["not_before"])
        self.assertEqual(cert.get_notAfter(), cert_dict["not_after"])
        self.assertEqual(cert.get_version(), cert_dict["version"])
        self.assertEqual(str(cert.get_serial_number()), cert_dict["serial_number"])
        self.assertEqual(cert.get_subject().CN, cert_dict["subject_cn"])
        self.assertEqual(cert.get_subject().OU, cert_dict["subject_ou"])
        self.assertEqual(cert.get_subject().O, cert_dict["subject_o"])
        self.assertEqual(cert.get_subject().C, cert_dict["subject_c"])
        self.assertEqual(cert.get_subject().ST, cert_dict["subject_st"])
        self.assertEqual(cert.get_subject().L, cert_dict["subject_l"])
        self.assertEqual(cert.get_subject().emailAddress, cert_dict["subject_e"])

    def test_database_file(self):
        """Tests creating a database file if it does not exist."""
        # make a temporary root dir
        temp_dir = tempfile.mkdtemp()
        dbpath = os.path.join(temp_dir, 'db.sqlite3')
        self.datastore.dbpath = os.path.join(dbpath)

        # test creating a db file
        self.datastore.get_certificate(1000)
        self.assertTrue(os.path.isfile(dbpath))

        # restore root dir
        shutil.rmtree(temp_dir)

    def test_add_certificate(self):
        """Tests adding a certificate to the datastore."""
        # create the CA with just a common name
        issuer_nick = "example_ca"
        profile_nick = "example_cert"
        (cacert, cakey, cacrl) = x509.create_ca(x509.Name("A"), 2048, 365 * 10)

        with mock.patch.object(self.datastore, "_connect", self.conn_mock):
            # add the certificate
            self.datastore.add_certificate(issuer_nick, profile_nick, cacert, "active", "ca")
            cert_dict = self.datastore.get_certificate(cacert.get_serial_number())
            self.assertEqualCert(issuer_nick, profile_nick, cacert, cert_dict, "active", "ca")

            # make sure adding a certificate twice (same serial number) fails
            with self.assertRaises(DataStoreError):
                self.datastore.add_certificate(issuer_nick, profile_nick, cacert, "active", "ca")

            # check a subca and all the name fields are good
            name = x509.Name("AAAA", "BBBB", "CCCCC", "DD", "EEEE", "FFFF", "G@G.COM")
            (subcert, subkey, subcrl) = x509.create_subca(cacert, cakey, name, 2048, 365)

            self.datastore.add_certificate(issuer_nick, profile_nick, subcert, "active", "subca")
            cert_dict = self.datastore.get_certificate(subcert.get_serial_number())
            self.assertEqualCert(issuer_nick, profile_nick, subcert, cert_dict, "active", "subca")

            # check an cert
            (cert, key) = x509.create_cert(cacert, cakey, x509.Name("RRR"), 2048, 365)
            self.datastore.add_certificate(issuer_nick, profile_nick, cert, "active", "cert")
            cert_dict = self.datastore.get_certificate(cert.get_serial_number())
            self.assertEqualCert(issuer_nick, profile_nick, cert, cert_dict, "active", "cert")

    def test_get_certificate(self):
        """Tests getting a certificate from the datastore."""
        with mock.patch.object(self.datastore, "_connect", self.conn_mock):
            # try getting a non-existant certificate
            cert_dict = self.datastore.get_certificate(111)
            self.assertIsNone(cert_dict)

            # add then get a certificate
            (cert, key, crl) = x509.create_ca(x509.Name("A"), 2048, 365)
            self.datastore.add_certificate("issuer_boom", "profile_clap", cert, "active", "ca")
            cert_dict = self.datastore.get_certificate(cert.get_serial_number())
            self.assertEqualCert("issuer_boom", "profile_clap", cert, cert_dict, "active", "ca")

    def test_revoke_certificate(self):
        """Tests revoking a certificate."""
        with mock.patch.object(self.datastore, "_connect", self.conn_mock):
            # add a certificate
            (cert, key, crl) = x509.create_ca(x509.Name("A"), 2048, 365)
            self.datastore.add_certificate("issuer_boom", "profile_clap", cert, "active", "ca")
            cert_dict = self.datastore.get_certificate(cert.get_serial_number())
            self.assertEqual("active", cert_dict["status"])

            # revoke the certificate
            self.datastore.revoke_certificate(cert.get_serial_number())

            # make sure status changed
            cert_dict = self.datastore.get_certificate(cert.get_serial_number())
            self.assertEqual("revoked", cert_dict["status"])

    def test_remove_certificate(self):
        """Tests removing a certificate."""
        with mock.patch.object(self.datastore, "_connect", self.conn_mock):
            # add a certificate
            (cert, key, crl) = x509.create_ca(x509.Name("A"), 2048, 365)
            self.datastore.add_certificate("issuer_boom", "profile_clap", cert, "active", "ca")
            cert_dict = self.datastore.get_certificate(cert.get_serial_number())
            self.assertEqual("active", cert_dict["status"])

            # remove the certificate
            self.datastore.remove_certificate(cert.get_serial_number())

            # make sure it is gone
            self.assertIsNone(self.datastore.get_certificate(cert.get_serial_number()))

    def test_list_certificates(self):
        """Tests listing certificates."""
        with mock.patch.object(self.datastore, "_connect", self.conn_mock):
            # make sure we get an empty list when the db is empty
            cert_list = self.datastore.list_certificates()
            self.assertListEqual(cert_list, [])

            # add a few certificates for issuer "issuer_boom"
            for i in range(10):
                cert = x509.create_ca(x509.Name("A{}".format(i)), 2048, 365)[0]
                self.datastore.add_certificate("issuer_boom", "profile_clap", cert, "active", "ca")

            # add a few certificates for another issuer
            for i in range(10):
                cert = x509.create_ca(x509.Name("B{}".format(i)), 2048, 365)[0]
                self.datastore.add_certificate("issuer_wham", "profile_wack", cert, "active", "ca")

            # list all the certificates
            cert_list = self.datastore.list_certificates()
            self.assertEqual(20, len(cert_list))
            names = [c["subject_cn"] for c in cert_list]
            names.sort()
            expected = ["A{}".format(i) for i in range(10)] + ["B{}".format(i) for i in range(10)]
            self.assertListEqual(names, expected)

            # list only "issuer_boom" certificates
            cert_list = self.datastore.list_certificates("issuer_boom")
            self.assertEqual(10, len(cert_list))
            names = [c["subject_cn"] for c in cert_list]
            expected = ["A{}".format(i) for i in range(10)]
            self.assertListEqual(names, expected)

            # make sure no items returned for a non-existent nickname
            cert_list = self.datastore.list_certificates("asdfasdf")
            self.assertListEqual(cert_list, [])

            # list only certificates for profile "profile_wack"
            cert_list = self.datastore.list_certificates(profile_nickname="profile_wack")
            self.assertEqual(10, len(cert_list))
            names = [c["subject_cn"] for c in cert_list]
            names.sort()
            expected = ["B{}".format(i) for i in range(10)]
            self.assertListEqual(names, expected)
