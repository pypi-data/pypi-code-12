#!/usr/bin/env python
"""Door Mouse certificate objects and helpers."""

import datetime
import pytz
import uuid
from OpenSSL import crypto

# constants
ALTTYPE_DNSNAME = "DNS"


class Name(object):
    """A Name object used as the Subject or Issuer in a certificate."""
    def __init__(self, cn, o=None, ou=None, c=None, st=None, l=None, e=None):
        """Inits the object."""
        self.cn = cn
        self.o = o
        self.ou = ou
        self.c = c
        self.st = st
        self.l = l
        self.e = e
        self.altnames = {(ALTTYPE_DNSNAME, self.cn)}

    def __str__(self):
        """Returns a str for the name."""
        fields = []
        if self.c:
            fields.append("C={}".format(self.c))
        if self.st:
            fields.append("ST={}".format(self.st))
        if self.l:
            fields.append("L={}".format(self.l))
        if self.o:
            fields.append("O={}".format(self.o))
        if self.ou:
            fields.append("OU={}".format(self.ou))
        if self.cn:
            fields.append("CN={}".format(self.cn))
        if self.e:
            fields.append("E={}".format(self.e))
        return ", ".join(fields)

    def add_altname(self, alt_type, alt_value):
        """Adds an Subject Alt Name to this name."""
        if alt_type != ALTTYPE_DNSNAME:
            raise ValueError("invalid subject alt name type '{}'".format(alt_type))
        self.altnames.add((alt_type, alt_value))

    def _copy_into_x509_name(self, x509_name):
        """Copies the name components into the x509_name object."""
        if self.cn:
            x509_name.CN = self.cn
        if self.o:
            x509_name.O = self.o
        if self.ou:
            x509_name.OU = self.ou
        if self.c:
            x509_name.C = self.c
        if self.st:
            x509_name.ST = self.st
        if self.l:
            x509_name.L = self.l
        if self.e:
            x509_name.emailAddress = self.e


def _create_basic_cert(subject_name, keysize, valid_days):
    """Returns a basic (certificate, key) with the features needed for most types of certificates."""
    # generate the key pair
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, keysize)

    # create the certificate and set the basics
    cert = crypto.X509()
    subject_name._copy_into_x509_name(cert.get_subject())
    cert.set_pubkey(key)
    cert.set_version(2)    # v3 is coded as literal 2, go figure

    # set the validity
    start = datetime.datetime.now(pytz.utc)
    end = start + datetime.timedelta(days=valid_days)
    cert.set_notBefore(start.strftime("%Y%m%d%H%M%SZ"))
    cert.set_notAfter(end.strftime("%Y%m%d%H%M%SZ"))

    # generate a unique serial number
    serial_number = uuid.uuid4().int
    cert.set_serial_number(serial_number)

    # set the subject key identifier extension
    cert.add_extensions([crypto.X509Extension("subjectKeyIdentifier", False, "hash", subject=cert)])

    # all done
    return (cert, key)


def create_ca(name, keysize, valid_days):
    """Returns (certificate, key, crl) for a self-signed CA with the given keysize."""
    # create the basic certificate
    (cert, key) = _create_basic_cert(name, keysize, valid_days)

    # set the issuer to self
    name._copy_into_x509_name(cert.get_issuer())

    # add the CA extensions
    cert.add_extensions([crypto.X509Extension("basicConstraints", True, "CA:TRUE")])
    cert.add_extensions([crypto.X509Extension("keyUsage", True, "keyCertSign, cRLSign")])
    cert.add_extensions([crypto.X509Extension("authorityKeyIdentifier", False, "keyid:always", issuer=cert)])

    # sign and return
    cert.sign(key, "sha256")
    return (cert, key, crypto.CRL())


def create_subca(ca_cert, ca_key, name, keysize, valid_days):
    """Returns (certificate, key, crl) for a subordinate CA signed by the given CA."""
    # create the basic certificate
    (cert, key) = _create_basic_cert(name, keysize, valid_days)

    # set the issuer
    cert.set_issuer(ca_cert.get_subject())

    # add the CA extensions
    cert.add_extensions([crypto.X509Extension("basicConstraints", True, "CA:TRUE")])
    cert.add_extensions([crypto.X509Extension("keyUsage", True, "keyCertSign, cRLSign")])
    cert.add_extensions([crypto.X509Extension("authorityKeyIdentifier", False, "keyid:always", issuer=ca_cert)])

    # sign the certifcate with the CA and return
    cert.sign(ca_key, "sha256")
    return (cert, key, crypto.CRL())


def create_cert(ca_cert, ca_key, name, keysize, valid_days):
    """Returns (certificate, key) for an cert signed by the given CA."""
    # create the basic certificate
    (cert, key) = _create_basic_cert(name, keysize, valid_days)

    # set the issuer
    cert.set_issuer(ca_cert.get_subject())

    # add the extensions
    cert.add_extensions([crypto.X509Extension("basicConstraints", True, "CA:FALSE")])
    cert.add_extensions([crypto.X509Extension("keyUsage", False, "digitalSignature")])
    cert.add_extensions([crypto.X509Extension("extendedKeyUsage", False, "clientAuth,serverAuth")])
    cert.add_extensions([crypto.X509Extension("authorityKeyIdentifier", False, "keyid:always", issuer=ca_cert)])

    altnames = ",".join(["{}:{}".format(t, v) for (t, v) in name.altnames])
    cert.add_extensions([crypto.X509Extension("subjectAltName", False, altnames)])

    # sign the certifcate with the CA and return
    cert.sign(ca_key, "sha256")
    return (cert, key)


def revoke(ca_crl, serial_number_hex):
    """Adds the serial number to the CRL."""
    rev = crypto.Revoked()
    rev.set_reason("unspecified")
    rev.set_rev_date(datetime.datetime.now(pytz.utc).strftime("%Y%m%d%H%M%SZ"))
    rev.set_serial(serial_number_hex)
    ca_crl.add_revoked(rev)


def sign(ca_cert, ca_key, request, valid_days):
    """Returns the signed certificate based on the request."""
    # create the certificate and set the basics
    cert = crypto.X509()
    cert.set_subject(request.get_subject())
    cert.set_pubkey(request.get_pubkey())
    cert.set_version(2)    # v3 is coded as literal 2, go figure

    # set the validity
    start = datetime.datetime.now(pytz.utc)
    end = start + datetime.timedelta(days=valid_days)
    cert.set_notBefore(start.strftime("%Y%m%d%H%M%SZ"))
    cert.set_notAfter(end.strftime("%Y%m%d%H%M%SZ"))

    # set the issuer
    cert.set_issuer(ca_cert.get_subject())

    # generate a unique serial number
    serial_number = uuid.uuid4().int
    cert.set_serial_number(serial_number)

    # add the extensions
    cert.add_extensions([crypto.X509Extension("subjectKeyIdentifier", False, "hash", subject=cert)])
    cert.add_extensions([crypto.X509Extension("basicConstraints", True, "CA:FALSE")])
    cert.add_extensions([crypto.X509Extension("keyUsage", False, "digitalSignature")])
    cert.add_extensions([crypto.X509Extension("extendedKeyUsage", False, "clientAuth,serverAuth")])
    cert.add_extensions([crypto.X509Extension("authorityKeyIdentifier", False, "keyid:always", issuer=ca_cert)])

    # all done
    cert.sign(ca_key, "sha256")
    return cert


def export_pem(cert, key):
    """Returns the cert and key in a string PEM format."""
    if cert:
        cert_pem = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
    else:
        cert_pem = None

    if key:
        key_pem = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)
    else:
        key_pem = None

    return (cert_pem, key_pem)


def days_till_expire(not_after):
    """Returns the number of days till the certificate expires, which may be zero or negative if already expired."""
    expires = datetime.datetime.strptime(not_after, "%Y%m%d%H%M%SZ")
    return (expires - datetime.datetime.now()).days
