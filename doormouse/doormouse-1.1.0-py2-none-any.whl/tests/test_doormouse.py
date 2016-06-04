#!/usr/bin/env python
import os
import unittest
import mock
import time
import sqlite3
import shutil
import tempfile
from OpenSSL import crypto
from doormouse import Doormouse
from doormouse.datastore import DataStore
from doormouse.filestore import FileStore
from doormouse import conf
from doormouse import x509


class TestDoormouse(unittest.TestCase):
    """Tests the doormouse api."""
    def setUp(self):
        """Sets up a datastore and filestore for individual tests."""
        # write all files to a temp directory
        self.rootdir = tempfile.mkdtemp()
        filestore = FileStore(self.rootdir)

        # used to mock the datastore
        self.conn = sqlite3.connect(":memory:")
        datastore = DataStore("", "")
        datastore._create_tables(self.conn)
        datastore._connect = mock.Mock(return_value=self.conn)

        # create the doormouse api object
        self.doormouse = Doormouse(filestore, datastore)

    def tearDown(self):
        """Tears down a datastore and filestore for individual tests."""
        self.conn.close()
        shutil.rmtree(self.rootdir)

    def assert_file_exists(self, cert_data):
        """Asserts the file for the certificate exists."""
        if not cert_data:
            raise AssertionError("certificate data is empty")

        elif cert_data["cert_type"] in ("ca", "subca"):
            path = self.doormouse.filestore._cert_path(cert_data["cert_type"], cert_data["profile_nickname"])
            if not os.path.isfile(os.path.join(path, "ca_{}.pem".format(cert_data["profile_nickname"]))):
                raise AssertionError("ca file for '{}' is not found".format(cert_data["profile_nickname"]))

            if not os.path.isfile(os.path.join(path, "key_{}.pem".format(cert_data["profile_nickname"]))):
                raise AssertionError("key file for '{}' is not found".format(cert_data["profile_nickname"]))

            if not os.path.isfile(os.path.join(path, "crl_{}.pem".format(cert_data["profile_nickname"]))):
                raise AssertionError("crl file for '{}' is not found".format(cert_data["profile_nickname"]))

        elif cert_data["cert_type"] == "cert":
            path = self.doormouse.filestore._cert_path(cert_data["cert_type"], cert_data["issuer_nickname"])
            if not os.path.isfile(os.path.join(path, "cert_{}.pem".format(cert_data["serial_number"]))):
                raise AssertionError("cert file for '{}' is not found".format(cert_data["serial_number"]))

            if not os.path.isfile(os.path.join(path, "key_{}.pem".format(cert_data["serial_number"]))):
                raise AssertionError("key file for '{}' is not found".format(cert_data["serial_number"]))

        else:
            raise AssertionError("unknown cert type '{}'".format(cert_data["cert_type"]))

    def test_initialize_single_ca(self):
        """Tests initializing an empty datastore with a single ca."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A"}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())
        self.doormouse.initialize_issuers(cnf)

        certs = self.doormouse.datastore.list_certificates()
        self.assertEqual(1, len(certs))
        self.assertEqual("a", certs[0]["issuer_nickname"])
        self.assertEqual("a", certs[0]["profile_nickname"])
        self.assertEqual("A", certs[0]["subject_cn"])
        self.assert_file_exists(certs[0])

    def test_initialize_multiple_ca(self):
        """Tests initializing an empty datastore with multiple ca."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A"}, {"nickname": "b", "cn": "B"}, {"nickname": "c", "cn": "C"}]}"""
        cnf = conf.parse(cstr)
        self.assertEqual([], self.doormouse.datastore.list_certificates())

        self.doormouse.initialize_issuers(cnf)
        self.assertEqual(3, len(self.doormouse.datastore.list_certificates()))

        for (nick, subj) in [("a", "A"), ("b", "B"), ("c", "C")]:
            certs = self.doormouse.datastore.list_certificates(profile_nickname=nick)
            self.assertEqual(1, len(certs))
            self.assertEqual(nick, certs[0]["issuer_nickname"])
            self.assertEqual(nick, certs[0]["profile_nickname"])
            self.assertEqual(subj, certs[0]["subject_cn"])
            self.assert_file_exists(certs[0])

    def test_initialize_single_ca_multiple_subca(self):
        """Tests initializing an empty datastore with a single ca and multiple ca."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A", "subca": [{"nickname": "b", "cn": "B"}, {"nickname": "c",
            "cn": "C"}, {"nickname": "d", "cn": "D"}]}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        self.doormouse.initialize_issuers(cnf)
        self.assertEqual(4, len(self.doormouse.datastore.list_certificates()))

        for (nick, subj) in [("b", "B"), ("c", "C"), ("d", "D")]:
            certs = self.doormouse.datastore.list_certificates(profile_nickname=nick)
            self.assertEqual(1, len(certs))
            self.assertEqual("a", certs[0]["issuer_nickname"])
            self.assertEqual(nick, certs[0]["profile_nickname"])
            self.assertEqual(subj, certs[0]["subject_cn"])
            self.assert_file_exists(certs[0])

    def test_initialize_new_subca(self):
        """Tests initializing an empty datastore with a single ca then later a single subca."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A"}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        self.doormouse.initialize_issuers(cnf)
        self.assertEqual(1, len(self.doormouse.datastore.list_certificates()))

        certs = self.doormouse.datastore.list_certificates()
        self.assertEqual(1, len(certs))
        self.assertEqual("a", certs[0]["issuer_nickname"])
        self.assertEqual("a", certs[0]["profile_nickname"])
        self.assertEqual("A", certs[0]["subject_cn"])
        self.assert_file_exists(certs[0])

        cstr = """{"ca": [{"nickname": "a", "cn": "A", "subca": [{"nickname": "b", "cn": "B"}]}]}"""
        cnf = conf.parse(cstr)
        self.doormouse.initialize_issuers(cnf)
        self.assertEqual(2, len(self.doormouse.datastore.list_certificates()))

        certs = self.doormouse.datastore.list_certificates(profile_nickname="a")
        self.assertEqual(1, len(certs))
        self.assertEqual("a", certs[0]["issuer_nickname"])
        self.assertEqual("a", certs[0]["profile_nickname"])
        self.assertEqual("A", certs[0]["subject_cn"])
        self.assert_file_exists(certs[0])

        certs = self.doormouse.datastore.list_certificates(profile_nickname="b")
        self.assertEqual(1, len(certs))
        self.assertEqual("a", certs[0]["issuer_nickname"])
        self.assertEqual("b", certs[0]["profile_nickname"])
        self.assertEqual("B", certs[0]["subject_cn"])
        self.assert_file_exists(certs[0])

    def test_initialize_new_ca(self):
        """Tests initializing an empty datastore with a single ca and then another ca."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A"}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        self.doormouse.initialize_issuers(cnf)
        self.assertEqual(1, len(self.doormouse.datastore.list_certificates()))

        certs = self.doormouse.datastore.list_certificates()
        self.assertEqual(1, len(certs))
        self.assertEqual("a", certs[0]["issuer_nickname"])
        self.assertEqual("a", certs[0]["profile_nickname"])
        self.assertEqual("A", certs[0]["subject_cn"])
        self.assert_file_exists(certs[0])

        cstr = """{"ca": [{"nickname": "a", "cn": "A"}, {"nickname": "b", "cn": "B"}]}"""
        cnf = conf.parse(cstr)
        self.doormouse.initialize_issuers(cnf)
        self.assertEqual(2, len(self.doormouse.datastore.list_certificates()))

        certs = self.doormouse.datastore.list_certificates(profile_nickname="a")
        self.assertEqual(1, len(certs))
        self.assertEqual("a", certs[0]["issuer_nickname"])
        self.assertEqual("a", certs[0]["profile_nickname"])
        self.assertEqual("A", certs[0]["subject_cn"])
        self.assert_file_exists(certs[0])

        certs = self.doormouse.datastore.list_certificates(profile_nickname="b")
        self.assertEqual(1, len(certs))
        self.assertEqual("b", certs[0]["issuer_nickname"])
        self.assertEqual("b", certs[0]["profile_nickname"])
        self.assertEqual("B", certs[0]["subject_cn"])
        self.assert_file_exists(certs[0])

    def test_initialize_multiple_ca_multiple_subca(self):
        """Tests initializing an empty datastore with multiple ca and multiple subca."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A", "subca": [{"nickname": "b", "cn": "B"}]}, {"nickname": "c",
            "cn": "C", "subca": [{"nickname": "d", "cn": "D"}]}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        self.doormouse.initialize_issuers(cnf)
        self.assertEqual(4, len(self.doormouse.datastore.list_certificates()))

        certs = self.doormouse.datastore.list_certificates(profile_nickname="a")
        self.assertEqual(1, len(certs))
        self.assertEqual("a", certs[0]["issuer_nickname"])
        self.assertEqual("a", certs[0]["profile_nickname"])
        self.assertEqual("A", certs[0]["subject_cn"])
        self.assert_file_exists(certs[0])

        certs = self.doormouse.datastore.list_certificates(profile_nickname="b")
        self.assertEqual(1, len(certs))
        self.assertEqual("a", certs[0]["issuer_nickname"])
        self.assertEqual("b", certs[0]["profile_nickname"])
        self.assertEqual("B", certs[0]["subject_cn"])
        self.assert_file_exists(certs[0])

        certs = self.doormouse.datastore.list_certificates(profile_nickname="c")
        self.assertEqual(1, len(certs))
        self.assertEqual("c", certs[0]["issuer_nickname"])
        self.assertEqual("c", certs[0]["profile_nickname"])
        self.assertEqual("C", certs[0]["subject_cn"])
        self.assert_file_exists(certs[0])

        certs = self.doormouse.datastore.list_certificates(profile_nickname="d")
        self.assertEqual(1, len(certs))
        self.assertEqual("c", certs[0]["issuer_nickname"])
        self.assertEqual("d", certs[0]["profile_nickname"])
        self.assertEqual("D", certs[0]["subject_cn"])
        self.assert_file_exists(certs[0])

    def test_create_just_cn(self):
        """Tests creating an cert with just a common name."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b"}]}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        self.doormouse.initialize_issuers(cnf)
        self.doormouse.create_cert(cnf, "b", "cn_boom")

        self.assertEqual(2, len(self.doormouse.datastore.list_certificates()))
        self.assertEqual(1, len(self.doormouse.datastore.list_certificates(profile_nickname="b")))
        cert = self.doormouse.datastore.list_certificates(profile_nickname="b")[0]
        self.assert_file_exists(cert)

    def test_create_missing_cert_cnf(self):
        """Tests creating an cert when the cert nickname does not exist."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b"}]}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        self.doormouse.initialize_issuers(cnf)

        with self.assertRaises(ValueError) as exc:
            self.doormouse.create_cert(cnf, "c", "cn_boom")
        self.assertEqual(1, len(self.doormouse.datastore.list_certificates()))

    def test_create_cert_altname(self):
        """Tests creating an cert with a common name and alt names."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b"}]}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        self.doormouse.initialize_issuers(cnf)
        self.doormouse.create_cert(cnf, "b", "cn_boom", ["alt1", "alt2"])

        self.assertEqual(2, len(self.doormouse.datastore.list_certificates()))
        self.assertEqual(1, len(self.doormouse.datastore.list_certificates(profile_nickname="b")))
        # cant really pull the altnames from an OpenSSL object to test whether it is correct
        cert = self.doormouse.datastore.list_certificates(profile_nickname="b")[0]
        self.assert_file_exists(cert)

    def test_create_cert_subca(self):
        """Tests creating an cert from a subca."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A", "subca": [{"nickname": "b", "cn": "B","cert":
            [{"nickname": "c"}]}]}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        self.doormouse.initialize_issuers(cnf)
        self.doormouse.create_cert(cnf, "c", "cn_boom", ["alt1", "alt2"])

        self.assertEqual(3, len(self.doormouse.datastore.list_certificates()))
        self.assertEqual(1, len(self.doormouse.datastore.list_certificates(profile_nickname="c")))
        # cant really pull the altnames from an OpenSSL object to test whether it is correct
        cert = self.doormouse.datastore.list_certificates(profile_nickname="c")[0]
        self.assert_file_exists(cert)

    def test_create_not_initialized(self):
        """Tests creating an cert when the ca has not been initialized."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b"}]}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        with self.assertRaises(ValueError) as exc:
            self.doormouse.create_cert(cnf, "b", "cn_boom")
        self.assertEqual(0, len(self.doormouse.datastore.list_certificates()))

    def test_list_empty(self):
        """Tests the list command when the datastore is empty."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A"}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())
        self.assertEqual([], self.doormouse.list_certificates(cnf))

        with self.assertRaises(ValueError) as exc:
            self.doormouse.list_certificates(cnf, "NON_EXISTENT_ISSUER")

    def test_list_cert(self):
        """Tests the list command when there are entities."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A"}, {"nickname": "b", "cn": "B", "cert": [{"nickname":"c"}]}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        self.doormouse.initialize_issuers(cnf)
        self.doormouse.create_cert(cnf, "c", "cn_boom")

        # this should return just the ca
        self.assertEqual(1, len(self.doormouse.list_certificates(cnf, "a")))
        self.assertEqual("A", self.doormouse.list_certificates(cnf, "a")[0]["subject_cn"])

        # this should return all of them
        certs = self.doormouse.list_certificates(cnf)
        self.assertEqual(3, len(certs))
        self.assertEqual({"A", "B", "cn_boom"}, {x["subject_cn"] for x in certs})

        # this should return CA "B" and cert "cn_boom"
        certs = self.doormouse.list_certificates(cnf, "b")
        self.assertEqual(2, len(certs))
        self.assertEqual({"B", "cn_boom"}, {x["subject_cn"] for x in certs})

    def test_revoke_certificate(self):
        """Tests revoking a certificate."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b"}]}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        # setup the certs
        self.doormouse.initialize_issuers(cnf)
        self.doormouse.create_cert(cnf, "b", "cn_boom")
        serial_number = self.doormouse.datastore.list_certificates(profile_nickname="b")[0]["serial_number"]

        # test a revoke with a non-existant serial number
        with self.assertRaises(ValueError) as exc:
            self.doormouse.revoke_certificate(cnf, "000")

        # test with a valid certificate
        self.doormouse.revoke_certificate(cnf, serial_number)

        # openssl sometimes has a zero prepended to their serial numbers
        (cacert, cakey, cacrl) = self.doormouse.filestore.load_ca("a")
        crl_serial = cacrl.get_revoked()[0].get_serial().lower()
        if crl_serial[0] == '0':
            cert_serial = "0{:x}".format(int(serial_number))
        else:
            cert_serial = "{:x}".format(int(serial_number))
        self.assertEqual(cert_serial, crl_serial)
        self.assertEqual("revoked", self.doormouse.datastore.get_certificate(serial_number)["status"])

        # try to revoke a certificate that is already revoked
        with self.assertRaises(ValueError) as exc:
            self.doormouse.revoke_certificate(cnf, serial_number)

    def test_refresh_crl_all(self):
        """Tests refreshing all the CRLs."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A"}, {"nickname": "b", "cn": "B"}, {"nickname": "c", "cn": "C"}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        # setup the certs
        self.doormouse.initialize_issuers(cnf)

        # at this time, there is no way to get the nextUpdate field in a CRL from OpenSSL
        # so we will check the data itself to make sure it changed
        files = []
        for profile in ("a", "b", "c"):
            path = self.doormouse.filestore._cert_path("ca", profile)
            with open(os.path.join(path, "crl_{}.pem".format(profile))) as f:
                files.append(f.read().strip())

        # sleep for a little bit to make sure the time changes
        time.sleep(2)

        self.doormouse.refresh_crl(cnf)

        newfiles = []
        for profile in ("a", "b", "c"):
            path = self.doormouse.filestore._cert_path("ca", profile)
            with open(os.path.join(path, "crl_{}.pem".format(profile))) as f:
                newfiles.append(f.read().strip())

        for i in range(3):
            self.assertNotEqual(files[i], newfiles[i])

    def test_refresh_crl_one(self):
        """Tests refreshing a single CRL."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A"}, {"nickname": "b", "cn": "B"}, {"nickname": "c", "cn": "C"}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        # setup the certs
        self.doormouse.initialize_issuers(cnf)

        # at this time, there is no way to get the nextUpdate field in a CRL from OpenSSL
        # so we will check the data itself to make sure it changed
        path = self.doormouse.filestore._cert_path("ca", "b")
        with open(os.path.join(path, "crl_b.pem")) as f:
            file_data = f.read().strip()

        # sleep for a little bit to make sure the time changes
        time.sleep(2)

        self.doormouse.refresh_crl(cnf, "b")

        with open(os.path.join(path, "crl_b.pem")) as f:
            new_data = f.read().strip()

        self.assertNotEqual(file_data, new_data)

        # try refreshing a non-existant issuer
        with self.assertRaises(ValueError) as exc:
            self.doormouse.refresh_crl(cnf, "NON_EXISTENT_NICKNAME")

    def test_list_revoked_one(self):
        """Tests listing the CRL of a single issuer."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b"}]}, {"nickname": "c",
            "cn": "C"}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        # setup the certs
        self.doormouse.initialize_issuers(cnf)
        self.doormouse.create_cert(cnf, "b", "cn_boom")
        serial_number = self.doormouse.datastore.list_certificates(profile_nickname="b")[0]["serial_number"]

        # run it with a non-existant issuer
        with self.assertRaises(ValueError) as exc:
            self.doormouse.list_revoked(cnf, "NON_EXISTENT_NICKNAME")
        self.assertEqual(0, len(self.doormouse.list_revoked(cnf)))

        # try to list an cert nickname
        with self.assertRaises(ValueError) as exc:
            self.doormouse.list_revoked(cnf, "b")
        self.assertEqual(0, len(self.doormouse.list_revoked(cnf)))

        # revoke the cert
        self.doormouse.revoke_certificate(cnf, serial_number)

        # get the revoked cert
        certs = self.doormouse.list_revoked(cnf, "a")
        self.assertEqual(1, len(certs))
        self.assertEqual("cn_boom", certs[0]["subject_cn"])

        # run it with an issuer that does not have anything revoked
        self.assertEqual(0, len(self.doormouse.list_revoked(cnf, "c")))

    def test_list_revoked_all(self):
        """Tests listing the CRL of all issuers."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b"}]}, {"nickname": "c",
            "cn": "C", "cert": [{"nickname": "d"}]}, {"nickname": "e", "cn": "E"}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        # setup the certs
        self.doormouse.initialize_issuers(cnf)
        self.doormouse.create_cert(cnf, "b", "cn_boom")
        self.doormouse.create_cert(cnf, "d", "cn_clap")
        serial_number_b = self.doormouse.datastore.list_certificates(profile_nickname="b")[0]["serial_number"]
        serial_number_d = self.doormouse.datastore.list_certificates(profile_nickname="d")[0]["serial_number"]

        # run the list command when nothing is revoked
        self.assertEqual(0, len(self.doormouse.list_revoked(cnf)))

        # revoke the certs
        self.doormouse.revoke_certificate(cnf, serial_number_b)
        self.doormouse.revoke_certificate(cnf, serial_number_d)
        certs = self.doormouse.list_revoked(cnf)
        self.assertEqual({"cn_boom", "cn_clap"}, {x["subject_cn"] for x in certs})

    def test_sign(self):
        """Tests signing a CSR."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b", "validity": 39}]}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        # setup the ca
        self.doormouse.initialize_issuers(cnf)

        # create a CSR
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 4096)
        req = crypto.X509Req()
        req.get_subject().CN = "A"
        req.get_subject().O = "B"
        req.get_subject().OU = "C"
        req.get_subject().C = "US"
        req.get_subject().ST = "E"
        req.get_subject().L = "F"
        req.get_subject().emailAddress = "g@g.com"
        req.set_pubkey(key)
        req.sign(key, "sha256")

        # save the CSR
        reqpath = os.path.join(self.rootdir, "test.csr")
        with open(reqpath, "w") as f:
            f.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, req))

        # try a non-existant cert
        with self.assertRaises(ValueError) as exc:
            self.doormouse.sign(cnf, "NON_EXISTENT_NICKNAME", reqpath)
        self.assertEqual(1, len(self.doormouse.datastore.list_certificates()))

        # try using a ca instead of cert
        with self.assertRaises(ValueError) as exc:
            self.doormouse.sign(cnf, "a", reqpath)
        self.assertEqual(1, len(self.doormouse.datastore.list_certificates()))

        # sign a request
        self.doormouse.sign(cnf, "b", reqpath)
        self.assertEqual(1, len(self.doormouse.datastore.list_certificates(profile_nickname="b")))

        certdata = self.doormouse.datastore.list_certificates(profile_nickname="b")[0]
        self.assertEqual(("A", "B", "C", "US", "E", "F", "g@g.com"), (req.get_subject().CN, req.get_subject().O,
            req.get_subject().OU, req.get_subject().C, req.get_subject().ST, req.get_subject().L,
            req.get_subject().emailAddress))
        certpath = self.doormouse.filestore._cert_path("cert", "a")
        self.assertTrue(os.path.isfile(os.path.join(certpath, "cert_{}.pem".format(certdata["serial_number"]))))

    def test_track(self):
        """Tests tracking an external certificate."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A"}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        # create a certificate for tracking
        name = x509.Name("A", "B", "C", "US", "E", "F", "g@g.com")
        (cacert, cakey, cacrl) = x509.create_ca(x509.Name("AAAA"), 2048, 365 * 10)
        (cert, key) = x509.create_cert(cacert, cakey, name, 2048, 365)
        certpath = os.path.join(self.rootdir, "test.pem")
        with open(certpath, "w") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

        # try tracking a file that does not exist
        with self.assertRaises(ValueError) as exc:
            self.doormouse.track(cnf, "FILE_DOES_NOT_EXIST.pem")
        self.assertEqual([], self.doormouse.datastore.list_certificates())

        # try tracking an actual cert
        self.doormouse.track(cnf, certpath)
        self.assertEqual(1, len(self.doormouse.datastore.list_certificates(profile_nickname="__tracked__")))
        cert = self.doormouse.datastore.list_certificates(profile_nickname="__tracked__")[0]

        self.assertEqual(("A", "B", "C", "US", "E", "F", "g@g.com"), (cert["subject_cn"], cert["subject_o"],
            cert["subject_ou"], cert["subject_c"], cert["subject_st"], cert["subject_l"], cert["subject_e"]))

    def test_remove_certificate(self):
        """Tests removing a certificate in the datastore."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b"}]}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        # create two certificates, one to forget and one not
        self.doormouse.initialize_issuers(cnf)
        self.doormouse.create_cert(cnf, "b", "cn_boom")
        self.doormouse.create_cert(cnf, "b", "cn_clap")
        serials = [c["serial_number"] for c in self.doormouse.datastore.list_certificates(profile_nickname="b")]

        # try forgetting a serial number that does not exist and make sure none are revoked
        with self.assertRaises(ValueError) as exc:
            self.doormouse.remove_certificate(cnf, "1")
        certs = self.doormouse.datastore.list_certificates(profile_nickname="b")
        for cert in certs:
            self.assertEqual("active", cert["status"])

        # forget one cert
        self.doormouse.remove_certificate(cnf, serials[0])
        self.assertIsNone(self.doormouse.datastore.get_certificate(serials[0]))
        self.assertIsNotNone(self.doormouse.datastore.get_certificate(serials[1]))

        # create a tracked cert and forget it
        (cacert, cakey, cacrl) = x509.create_ca(x509.Name("AAAA"), 2048, 365 * 10)
        (cert, key) = x509.create_cert(cacert, cakey, x509.Name("BBBB"), 2048, 365)
        certpath = os.path.join(self.rootdir, "test.pem")
        with open(certpath, "w") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

        self.doormouse.track(cnf, certpath)
        self.assertEqual(1, len(self.doormouse.datastore.list_certificates(profile_nickname="__tracked__")))
        serial = self.doormouse.datastore.list_certificates(profile_nickname="__tracked__")[0]["serial_number"]

        self.doormouse.remove_certificate(cnf, serial)
        self.assertIsNone(self.doormouse.datastore.get_certificate(serial))
        self.assertEqual(0, len(self.doormouse.datastore.list_certificates(profile_nickname="__tracked__")))

    def test_list_expiring(self):
        """Tests warning expiring certificates."""
        cstr = """{"ca": [{"nickname": "a", "cn": "A", "validity": 10, "cert": [{"nickname": "b",
            "validity": 10}]}]}"""
        cnf = conf.parse(cstr)

        self.assertEqual([], self.doormouse.datastore.list_certificates())

        # check expiring when there are no entries
        certs = self.doormouse.list_expiring(cnf, 1000)
        self.assertEqual([], certs)

        # add a few certificates
        self.doormouse.initialize_issuers(cnf)
        self.doormouse.create_cert(cnf, "b", "cn_boom")

        # there should be no certs expiring in 5 days
        certs = self.doormouse.list_expiring(cnf, 5)
        self.assertEqual([], certs)

        # both certificates expire in exactly 10 days
        certs = self.doormouse.list_expiring(cnf, 10)
        self.assertEqual({"A", "cn_boom"}, {x["subject_cn"] for x in certs})

        # both certificates expire with 30 days
        certs = self.doormouse.list_expiring(cnf, 30)
        self.assertEqual({"A", "cn_boom"}, {x["subject_cn"] for x in certs})
