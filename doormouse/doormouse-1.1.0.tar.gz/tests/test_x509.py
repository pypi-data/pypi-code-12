#!/usr/bin/env python
import unittest
import mock
import datetime
from OpenSSL import crypto
from OpenSSL import SSL
from doormouse import x509


class TestCert(unittest.TestCase):
    """Tests the cert functionality."""
    def setUp(self):
        pass

    def assertNameFields(self, name, cn, o, ou, altnames, c, st, l, e):
        """Asserts that the name object is equal to all the fields."""
        if name.cn != cn:
            raise AssertionError("common name '{}' != '{}'".format(name.cn, cn))
        if name.o != o:
            raise AssertionError("organization '{}' != '{}'".format(name.o, o))
        if name.ou != ou:
            raise AssertionError("organizational unit '{}' != '{}'".format(name.ou, ou))
        if name.c != c:
            raise AssertionError("country '{}' != '{}'".format(name.c, c))
        if name.st != st:
            raise AssertionError("state or province '{}' != '{}'".format(name.st, st))
        if name.l != l:
            raise AssertionError("locality '{}' != '{}'".format(name.l, l))
        if name.e != e:
            raise AssertionError("email address '{}' != '{}'".format(name.e, e))
        self.assertSetEqual(name.altnames, altnames)

    def assertEqualName(self, x509_name, name):
        """Asserts that the OpenSSL x509 name is equal to the lib name."""
        if name.cn != x509_name.CN:
            raise AssertionError("common name '{}' != '{}'".format(x509_name.CN, name.cn))
        if name.o != x509_name.O:
            raise AssertionError("organization '{}' != '{}'".format(x509_name.O, name.o))
        if name.ou != x509_name.OU:
            raise AssertionError("organizational unit '{}' != '{}'".format(x509_name.OU, name.ou))
        if name.c != x509_name.C:
            raise AssertionError("country '{}' != '{}'".format(x509_name.C, name.c))
        if name.st != x509_name.ST:
            raise AssertionError("state or province '{}' != '{}'".format(x509_name.ST, name.st))
        if name.l != x509_name.L:
            raise AssertionError("locality '{}' != '{}'".format(x509_name.L, name.l))
        if name.e != x509_name.emailAddress:
            raise AssertionError("email address '{}' != '{}'".format(x509_name.emailAddress, name.e))

    def assertHasExtension(self, cert, name, critical):
        """Asserts that the x509 certificate has the extension."""
        for i in range(cert.get_extension_count()):
            ext = cert.get_extension(i)
            if ext.get_short_name() == name:
                if ext.get_critical() != critical:
                    raise AssertionError("ext '{}' critical '{}' != '{}'".format(name, ext.get_critical(), critical))
                return
        raise AssertionError("ext '{}' not found in certificate".format(name))

    def test_name(self):
        """Tests creating a name object."""
        # just a common name
        name = x509.Name("alpha")
        alts = {(x509.ALTTYPE_DNSNAME, "alpha")}
        parts = [name, "alpha", None, None, alts, None, None, None, None]
        self.assertNameFields(*parts)

        # add the org
        name = x509.Name("alpha", "bravo")
        alts = {(x509.ALTTYPE_DNSNAME, "alpha")}
        parts = [name, "alpha", "bravo", None, alts, None, None, None, None]
        self.assertNameFields(*parts)

        # add the org unit
        name = x509.Name("alpha", "bravo", "charlie")
        alts = {(x509.ALTTYPE_DNSNAME, "alpha")}
        parts = [name, "alpha", "bravo", "charlie", alts, None, None, None, None]
        self.assertNameFields(*parts)

        # add all the other components
        name = x509.Name("A", "B", "C", "D", "E", "F", "G")
        alts = {(x509.ALTTYPE_DNSNAME, "A")}
        parts = [name, "A", "B", "C", alts, "D", "E", "F", "G"]
        self.assertNameFields(*parts)

    def test_altnames(self):
        """Tests altnames."""
        # just the default alt name
        name = x509.Name("A")
        alts = {(x509.ALTTYPE_DNSNAME, "A")}
        parts = [name, "A", None, None, alts, None, None, None, None]
        self.assertNameFields(*parts)

        # add a single alt name
        name = x509.Name("A")
        name.add_altname(x509.ALTTYPE_DNSNAME, "B")
        alts = {(x509.ALTTYPE_DNSNAME, "A"), (x509.ALTTYPE_DNSNAME, "B")}
        parts = [name, "A", None, None, alts, None, None, None, None]
        self.assertNameFields(*parts)

        # try adding an alt name of a bad type
        name = x509.Name("A")
        with self.assertRaises(ValueError):
            name.add_altname("asdfasdf", "B")

        # add a few alt names
        name = x509.Name("A")
        name.add_altname(x509.ALTTYPE_DNSNAME, "B")
        name.add_altname(x509.ALTTYPE_DNSNAME, "C")
        name.add_altname(x509.ALTTYPE_DNSNAME, "D")
        alts = {(x509.ALTTYPE_DNSNAME, "D"), (x509.ALTTYPE_DNSNAME, "C"), (x509.ALTTYPE_DNSNAME, "B"),
            (x509.ALTTYPE_DNSNAME, "A")}
        parts = [name, "A", None, None, alts, None, None, None, None]
        self.assertNameFields(*parts)

    def test_create_ca(self):
        """Tests the creation of a CA."""
        # data for the certificate
        name = x509.Name("A")
        valid_days = 365 * 10
        before = "20141105145523Z"
        after = "20241102145523Z"

        # create the cert with mock dates
        with mock.patch.object(x509.datetime, "datetime", mock.Mock(wraps=datetime.datetime)) as patched:
            patched.now.return_value = datetime.datetime.strptime(before, "%Y%m%d%H%M%SZ")
            (cert, key, crl) = x509.create_ca(name, 2048, valid_days)

        # check the basic fields
        self.assertEqual(2, cert.get_version())
        self.assertEqual(before, cert.get_notBefore())
        self.assertEqual(after, cert.get_notAfter())
        self.assertEqual("sha256WithRSAEncryption", cert.get_signature_algorithm())

        # check the names
        self.assertEqualName(cert.get_issuer(), name)
        self.assertEqualName(cert.get_subject(), name)

        # check the extensions
        self.assertHasExtension(cert, "subjectKeyIdentifier", False)
        self.assertHasExtension(cert, "authorityKeyIdentifier", False)
        self.assertHasExtension(cert, "basicConstraints", True)
        self.assertHasExtension(cert, "keyUsage", True)
        self.assertEqual(4, cert.get_extension_count())

        # check the key
        #self.assertEqual(crypto.TYPE_RSA, key.type())
        self.assertEqual(2048, key.bits())

        ctx = SSL.Context(SSL.TLSv1_METHOD)
        ctx.use_privatekey(key)
        ctx.use_certificate(cert)
        try:
            ctx.check_privatekey()
        except SSL.Error:
            raise AssertionError("private key is not valid for the certificate")

    def test_create_subca(self):
        """Tests the creation of a subordinate CA."""
        # create the ca first
        ca_name = x509.Name("A")
        (ca_cert, ca_key, ca_crl) = x509.create_ca(ca_name, 2048, 365 * 10)

        # create the sub cert with mock dates
        name = x509.Name("B")
        valid_days = 365 * 10
        before = "20141105145523Z"
        after = "20241102145523Z"

        with mock.patch.object(x509.datetime, "datetime", mock.Mock(wraps=datetime.datetime)) as patched:
            patched.now.return_value = datetime.datetime.strptime(before, "%Y%m%d%H%M%SZ")
            (cert, key, crl) = x509.create_subca(ca_cert, ca_key, name, 2048, valid_days)

        # check the basic fields
        self.assertEqual(2, cert.get_version())
        self.assertEqual(before, cert.get_notBefore())
        self.assertEqual(after, cert.get_notAfter())
        self.assertEqual("sha256WithRSAEncryption", cert.get_signature_algorithm())

        # check the names
        self.assertEqualName(cert.get_issuer(), ca_name)
        self.assertEqualName(cert.get_subject(), name)

        # check the extensions
        self.assertHasExtension(cert, "subjectKeyIdentifier", False)
        self.assertHasExtension(cert, "authorityKeyIdentifier", False)
        self.assertHasExtension(cert, "basicConstraints", True)
        self.assertHasExtension(cert, "keyUsage", True)
        self.assertEqual(4, cert.get_extension_count())

        # check the key
        #self.assertEqual(crypto.TYPE_RSA, key.type())
        self.assertEqual(2048, key.bits())

        ctx = SSL.Context(SSL.TLSv1_METHOD)
        ctx.use_privatekey(key)
        ctx.use_certificate(cert)
        try:
            ctx.check_privatekey()
        except SSL.Error:
            raise AssertionError("private key is not valid for the certificate")

    def test_create_cert(self):
        """Tests the creation of an cert certificate."""
        # create the ca first
        ca_name = x509.Name("A")
        (ca_cert, ca_key, ca_crl) = x509.create_ca(ca_name, 2048, 365 * 10)

        # create the cert cert with mock dates
        name = x509.Name("B")
        valid_days = 365 * 10
        before = "20141105145523Z"
        after = "20241102145523Z"

        with mock.patch.object(x509.datetime, "datetime", mock.Mock(wraps=datetime.datetime)) as patched:
            patched.now.return_value = datetime.datetime.strptime(before, "%Y%m%d%H%M%SZ")
            (cert, key) = x509.create_cert(ca_cert, ca_key, name, 2048, valid_days)

        # check the basic fields
        self.assertEqual(2, cert.get_version())
        self.assertEqual(before, cert.get_notBefore())
        self.assertEqual(after, cert.get_notAfter())
        self.assertEqual("sha256WithRSAEncryption", cert.get_signature_algorithm())

        # check the names
        self.assertEqualName(cert.get_issuer(), ca_name)
        self.assertEqualName(cert.get_subject(), name)

        # check the extensions
        self.assertHasExtension(cert, "subjectKeyIdentifier", False)
        self.assertHasExtension(cert, "authorityKeyIdentifier", False)
        self.assertHasExtension(cert, "basicConstraints", True)
        self.assertHasExtension(cert, "keyUsage", False)
        self.assertHasExtension(cert, "extendedKeyUsage", False)
        self.assertHasExtension(cert, "subjectAltName", False)
        self.assertEqual(6, cert.get_extension_count())

        # check the key
        #self.assertEqual(crypto.TYPE_RSA, key.type())
        self.assertEqual(2048, key.bits())

        ctx = SSL.Context(SSL.TLSv1_METHOD)
        ctx.use_privatekey(key)
        ctx.use_certificate(cert)
        try:
            ctx.check_privatekey()
        except SSL.Error:
            raise AssertionError("private key is not valid for the certificate")

    def test_days_till_expire(self):
        """Tests the calculation of days left till expiration."""
        (ca_cert, ca_key, ca_crl) = x509.create_ca(x509.Name("A"), 2048, 365 * 10)

        # here are the dates we will use to test it
        valid_days = 5
        created = "2015-01-01 12:03:12"
        day_expires = "2015-01-06"
        day_still_valid = "2015-01-04"
        day_already_expired = "2015-01-09"

        # create the cert cert with mock dates
        with mock.patch.object(x509.datetime, "datetime", mock.Mock(wraps=datetime.datetime)) as patched:
            patched.now.return_value = datetime.datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
            (cert, key) = x509.create_cert(ca_cert, ca_key, x509.Name("B"), 2048, valid_days)

        # test when the cert has not yet expired
        with mock.patch.object(x509.datetime, "datetime", mock.Mock(wraps=datetime.datetime)) as patched:
            patched.now.return_value = datetime.datetime.strptime(day_still_valid, "%Y-%m-%d")
            self.assertEqual(2, x509.days_till_expire(cert.get_notAfter()))

        # test the day of expiration
        with mock.patch.object(x509.datetime, "datetime", mock.Mock(wraps=datetime.datetime)) as patched:
            patched.now.return_value = datetime.datetime.strptime(day_expires, "%Y-%m-%d")
            self.assertEqual(0, x509.days_till_expire(cert.get_notAfter()))

        # test already expired
        with mock.patch.object(x509.datetime, "datetime", mock.Mock(wraps=datetime.datetime)) as patched:
            patched.now.return_value = datetime.datetime.strptime(day_already_expired, "%Y-%m-%d")
            self.assertEqual(-3, x509.days_till_expire(cert.get_notAfter()))

    def test_revoke(self):
        """Tests revoking a certificate."""
        # revoke a certificate with some mock date
        (ca_cert, ca_key, ca_crl) = x509.create_ca(x509.Name("A"), 2048, 365 * 10)
        serial_hex = "DEADBEEF"
        revoked_date = "20140102123455Z"
        with mock.patch.object(x509.datetime, "datetime", mock.Mock(wraps=datetime.datetime)) as patched:
            patched.now.return_value = datetime.datetime.strptime(revoked_date, "%Y%m%d%H%M%SZ")
            x509.revoke(ca_crl, serial_hex)

        self.assertEqual(1, len(ca_crl.get_revoked()))
        self.assertEqual(serial_hex, ca_crl.get_revoked()[0].get_serial())
        self.assertEqual(revoked_date, ca_crl.get_revoked()[0].get_rev_date())
        self.assertEqual("Unspecified", ca_crl.get_revoked()[0].get_reason())

        # revoke 10 certificates
        (ca_cert, ca_key, ca_crl) = x509.create_ca(x509.Name("A"), 2048, 365 * 10)
        serial_hex = "DEADBEEF{}FEADBEE"
        revoked_date = "2014010203100{}Z"

        for i in range(10):
            with mock.patch.object(x509.datetime, "datetime", mock.Mock(wraps=datetime.datetime)) as patched:
                patched.now.return_value = datetime.datetime.strptime(revoked_date.format(i), "%Y%m%d%H%M%SZ")
                x509.revoke(ca_crl, serial_hex.format(i))

        self.assertEqual(10, len(ca_crl.get_revoked()))
        for i in range(10):
            self.assertEqual(serial_hex.format(i), ca_crl.get_revoked()[i].get_serial())
            self.assertEqual(revoked_date.format(i), ca_crl.get_revoked()[i].get_rev_date())
            self.assertEqual("Unspecified", ca_crl.get_revoked()[i].get_reason())

    def test_sign(self):
        """Tests signing a certificate signing request."""
        # create a CA and an OpenSSL CSR
        (ca_cert, ca_key, ca_crl) = x509.create_ca(x509.Name("A"), 2048, 365 * 10)

        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        req = crypto.X509Req()
        req.get_subject().CN = "B"
        req.set_pubkey(key)
        req.sign(key, "sha256")

        # sign it with mock dates
        before = "20141105145523Z"
        after = "20241102145523Z"
        valid_days = 365 * 10

        with mock.patch.object(x509.datetime, "datetime", mock.Mock(wraps=datetime.datetime)) as patched:
            patched.now.return_value = datetime.datetime.strptime(before, "%Y%m%d%H%M%SZ")
            cert = x509.sign(ca_cert, ca_key, req, valid_days)

        # check the basic fields
        self.assertEqual(2, cert.get_version())
        self.assertEqual(before, cert.get_notBefore())
        self.assertEqual(after, cert.get_notAfter())
        self.assertEqual("sha256WithRSAEncryption", cert.get_signature_algorithm())

        # check the names
        self.assertEqualName(cert.get_issuer(), x509.Name("A"))
        self.assertEqualName(cert.get_subject(), x509.Name("B"))

        # check the extensions
        self.assertHasExtension(cert, "subjectKeyIdentifier", False)
        self.assertHasExtension(cert, "authorityKeyIdentifier", False)
        self.assertHasExtension(cert, "basicConstraints", True)
        self.assertHasExtension(cert, "keyUsage", False)
        self.assertHasExtension(cert, "extendedKeyUsage", False)
        self.assertEqual(5, cert.get_extension_count())

        # check the key metadata
        #self.assertEqual(crypto.TYPE_RSA, key.type())
        self.assertEqual(2048, key.bits())

    def test_export(self):
        """Tests exporting a key and certificate."""
        test_cert = "-----BEGIN CERTIFICATE-----"
        test_key = "-----BEGIN PRIVATE KEY-----"

        # create the ca first
        ca_name = x509.Name("A")
        (ca_cert, ca_key, ca_crl) = x509.create_ca(ca_name, 2048, 365 * 10)

        # create the cert with mock dates
        (cert, key) = x509.create_cert(ca_cert, ca_key, x509.Name("B"), 2048, 365 * 10)

        # try exporting
        (cert_pem, key_pem) = x509.export_pem(cert, key)
        self.assertEqual(test_cert, cert_pem[:len(test_cert)])
        self.assertEqual(test_key[:11], key_pem[:11])
        self.assertEqual(test_key[-16:], key_pem[-17:-1])

        # alternate missing parts
        (cert_pem, key_pem) = x509.export_pem(None, key)
        self.assertIsNone(cert_pem)
        self.assertEqual(test_key[:11], key_pem[:11])
        self.assertEqual(test_key[-16:], key_pem[-17:-1])

        (cert_pem, key_pem) = x509.export_pem(cert, None)
        self.assertEqual(test_cert, cert_pem[:len(test_cert)])
        self.assertIsNone(key_pem)

        self.assertEqual((None, None), x509.export_pem(None, None))
