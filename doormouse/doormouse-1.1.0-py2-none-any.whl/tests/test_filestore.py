#!/usr/bin/env python
import unittest
import os.path
import tempfile
import shutil
from OpenSSL import crypto
from doormouse import x509
from doormouse.filestore import FileStore, FileStoreError


class TestFilestore(unittest.TestCase):
    """Tests the filestore functionality."""
    def setUp(self):
        self.rootdir = tempfile.mkdtemp()
        self.filestore = FileStore(self.rootdir)

    def tearDown(self):
        shutil.rmtree(self.rootdir)

    def assertX509Files(self, cert_type, profile_nickname, cert, key=None, crl=None, crl_valid_for=None):
        """Asserts whether the cert, key, and crl in the filestore are equal to the ones given."""
        path = self.filestore._cert_path(cert_type, profile_nickname)

        if cert_type == "ca":
            # cert
            pem_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
            try:
                with open(os.path.join(path, "ca_{}.pem".format(profile_nickname)), "r") as f:
                    data = f.read()
            except IOError as e:
                raise AssertionError("error reading cert file for '{}': {}".format(profile_nickname, e))
            self.assertEqual(pem_cert.strip(), data.strip())

            # key
            pem_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)
            try:
                with open(os.path.join(path, "key_{}.pem".format(profile_nickname)), "r") as f:
                    data = f.read()
            except IOError as e:
                raise AssertionError("error reading key file for '{}': {}".format(profile_nickname, e))
            self.assertEqual(pem_key.strip(), data.strip())

            # crl
            self.assertX509Crl(cert_type, profile_nickname, cert, key, crl, crl_valid_for)

        elif cert_type == "cert":
            # cert
            pem_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
            try:
                with open(os.path.join(path, "cert_{}.pem".format(cert.get_serial_number())), "r") as f:
                    data = f.read()
            except IOError as e:
                raise AssertionError("error reading cert file for '{}': {}".format(profile_nickname, e))
            self.assertEqual(pem_cert.strip(), data.strip())

            # key
            if key:
                pem_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)
                try:
                    with open(os.path.join(path, "key_{}.pem".format(cert.get_serial_number())), "r") as f:
                        data = f.read()
                except IOError as e:
                    raise AssertionError("error reading key file for '{}': {}".format(profile_nickname, e))
                self.assertEqual(pem_key.strip(), data.strip())

        else:
            raise AssertionError("unknown cert_type: {}".format(cert_type))

    def assertX509Crl(self, cert_type, profile_nickname, cert, key, crl, crl_valid_for):
        """Asserts whether the crl in the filestore is equal to the given one."""
        path = self.filestore._cert_path(cert_type, profile_nickname)
        pem_crl = crl.export(cert, key, type=crypto.FILETYPE_PEM, days=crl_valid_for)
        try:
            with open(os.path.join(path, "crl_{}.pem".format(profile_nickname)), "r") as f:
                data = f.read()
        except IOError as e:
            raise AssertionError("error reading crl file for '{}': {}".format(profile_nickname, e))
            self.assertEqual(pem_crl.strip(), data.strip())

    def assertX509Objects(self, cert1, cert2, key1, key2, crl1=None, crl2=None):
        """Asserts whether the certs, keys, and optionally the crls are the same."""
        # cert
        str_cert1 = crypto.dump_certificate(crypto.FILETYPE_PEM, cert1)
        str_cert2 = crypto.dump_certificate(crypto.FILETYPE_PEM, cert2)
        if str_cert1.strip() != str_cert2.strip():
            raise AssertionError("cert1 != cert2")

        # key
        str_key1 = crypto.dump_privatekey(crypto.FILETYPE_PEM, key1)
        str_key2 = crypto.dump_privatekey(crypto.FILETYPE_PEM, key2)
        if str_key1.strip() != str_key2.strip():
            raise AssertionError("key1 != key2")

        # crl
        str_crl1 = crl1.export(cert1, key1, type=crypto.FILETYPE_PEM, days=100)
        str_crl2 = crl2.export(cert2, key2, type=crypto.FILETYPE_PEM, days=100)
        if str_crl1.strip() != str_crl2.strip():
            raise AssertionError("crl1 != crl2")

    def test_store_ca(self):
        """Tests storing a CA."""
        # try a CA
        profile_nickname = "boom"
        crl_valid_for = 120
        (cert, key, crl) = x509.create_ca(x509.Name("A"), 2048, 365 * 10)
        self.filestore.store_ca(profile_nickname, cert, key, crl, crl_valid_for)
        self.assertX509Files("ca", profile_nickname, cert, key, crl, crl_valid_for)

        # try a Sub CA
        profile_nickname = "beef"
        crl_valid_for = 120
        (cacert, cakey, cacrl) = x509.create_ca(x509.Name("A"), 2048, 365 * 10)
        (cert, key, crl) = x509.create_subca(cacert, cakey, x509.Name("B"), 2048, 365 * 10)
        self.filestore.store_ca(profile_nickname, cert, key, crl, crl_valid_for)
        self.assertX509Files("ca", profile_nickname, cert, key, crl, crl_valid_for)

    def test_store_crl(self):
        """Test storing the crl."""
        # try a CA
        profile_nickname = "boom"
        crl_valid_for = 120
        (cert, key, crl) = x509.create_ca(x509.Name("A"), 2048, 365 * 10)
        self.filestore.store_crl(profile_nickname, cert, key, crl, crl_valid_for)
        self.assertX509Crl("ca", profile_nickname, cert, key, crl, crl_valid_for)

        # try a Sub CA
        profile_nickname = "beef"
        crl_valid_for = 120
        (cacert, cakey, cacrl) = x509.create_ca(x509.Name("A"), 2048, 365 * 10)
        (cert, key, crl) = x509.create_subca(cacert, cakey, x509.Name("B"), 2048, 365 * 10)
        self.filestore.store_crl(profile_nickname, cert, key, crl, crl_valid_for)
        self.assertX509Crl("ca", profile_nickname, cert, key, crl, crl_valid_for)

    def test_load_ca(self):
        """Tests loading a CA."""
        # try a CA
        profile_nickname = "abcd"
        crl_valid_for = 120
        (cacert, cakey, cacrl) = x509.create_ca(x509.Name("A"), 2048, 365 * 10)
        self.filestore.store_ca(profile_nickname, cacert, cakey, cacrl, crl_valid_for)
        (rcert, rkey, rcrl) = self.filestore.load_ca(profile_nickname)
        self.assertX509Objects(rcert, cacert, rkey, cakey, rcrl, cacrl)

        # try a Sub CA
        profile_nickname = "rooty"
        crl_valid_for = 120
        (cert, key, crl) = x509.create_subca(cacert, cakey, x509.Name("B"), 2048, 365 * 10)
        self.filestore.store_ca(profile_nickname, cert, key, crl, crl_valid_for)
        (rcert, rkey, rcrl) = self.filestore.load_ca(profile_nickname)
        self.assertX509Objects(rcert, cert, rkey, key, rcrl, crl)

    def test_store_cert(self):
        """Tests storing an cert."""
        (cacert, cakey, cacrl) = x509.create_ca(x509.Name("A"), 2048, 365 * 10)

        # test storing a cert and key
        issuer_nickname = "boom"
        (cert, key) = x509.create_cert(cacert, cakey, x509.Name("B"), 2048, 365)
        self.filestore.store_cert(issuer_nickname, cert, key)
        self.assertX509Files("cert", issuer_nickname, cert, key)

        # test storing just a cert
        (cert, key) = x509.create_cert(cacert, cakey, x509.Name("C"), 2048, 365)
        self.filestore.store_cert(issuer_nickname, cert)
        self.assertX509Files("cert", issuer_nickname, cert)

    def test_load_cert(self):
        """Tests loading a certificate cert."""
        # create the certificate
        (cacert, cakey, cacrl) = x509.create_ca(x509.Name("A"), 2048, 365 * 10)
        (cert, key) = x509.create_cert(cacert, cakey, x509.Name("B"), 2048, 365)
        certpath = os.path.join(self.rootdir, "test.pem")
        with open(certpath, "w") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

        # load it
        cert = self.filestore.load_cert(certpath)
        self.assertEqual("B", cert.get_subject().CN)

        # load a file that is not an cert
        with self.assertRaises(FileStoreError):
            self.filestore.load_cert("/etc/passwd")

    def test_load_request(self):
        """Tests loading a certificate request (CSR)."""
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

        # load the CSR
        req = self.filestore.load_request(reqpath)
        self.assertEqual(("A", "B", "C", "US", "E", "F", "g@g.com"), (req.get_subject().CN, req.get_subject().O,
            req.get_subject().OU, req.get_subject().C, req.get_subject().ST, req.get_subject().L,
            req.get_subject().emailAddress))

        # load a file that is not a CSR
        with self.assertRaises(FileStoreError):
            self.filestore.load_request("/etc/passwd")
