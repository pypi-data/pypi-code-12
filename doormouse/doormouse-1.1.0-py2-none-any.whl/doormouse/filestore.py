#!/usr/bin/env python
"""Provides filestore access."""
import os
from OpenSSL import crypto
from . import FileStoreError
from . import x509


class FileStore(object):
    def __init__(self, rootdir):
        self.rootdir = rootdir

    def _cert_path(self, cert_type, profile_nickname):
        """Returns the path to the cert."""
        if cert_type in ("ca", "subca"):
            return os.path.abspath(os.path.join(self.rootdir, "ca", profile_nickname))
        elif cert_type == "cert":
            return os.path.abspath(os.path.join(self.rootdir, "cert", profile_nickname))
        else:
            raise FileStoreError("unknown cert type '{}'".format(cert_type))

    def _setup_directory(self, cert_type, profile_nickname):
        """Creates the directory for profile_nickname."""
        if not cert_type in ("ca", "cert"):
            raise FileStoreError("unknown cert type '{}'".format(cert_type))

        if not os.path.isdir(self.rootdir):
            os.mkdir(self.rootdir)
        if not os.path.isdir(os.path.join(self.rootdir, cert_type)):
            os.mkdir(os.path.join(self.rootdir, cert_type))
        if not os.path.isdir(os.path.join(self.rootdir, cert_type, profile_nickname)):
            os.mkdir(os.path.join(self.rootdir, cert_type, profile_nickname))

        return self._cert_path(cert_type, profile_nickname)

    def initialize_store(self):
        """Initializes the store, throws FileStoreError on error."""
        try:
            if not os.path.isdir(self.rootdir):
                os.mkdir(self.rootdir)
        except OSError as exc:
            raise FileStoreError("unable to create file store directory '{}': {}".format(self.rootdir, exc.strerror))

        if not os.access(self.rootdir, os.W_OK):
            raise FileStoreError("unable to write to file store directory '{}'".format(self.rootdir))

    def store_ca(self, profile_nickname, cert, key, crl, crl_valid_for):
        """Stores the CA components as files in the filestore."""
        path = self._setup_directory("ca", profile_nickname)

        try:
            (cert_pem, key_pem) = x509.export_pem(cert, key)

            # cert
            with open(os.path.join(path, "ca_{}.pem".format(profile_nickname)), "w") as f:
                f.write(cert_pem)
                f.write("\n")

            # key
            with open(os.path.join(path, "key_{}.pem".format(profile_nickname)), "w") as f:
                f.write(key_pem)
                f.write("\n")
        except IOError as exc:
            raise FileStoreError("Error reading cert data: {}".format(exc.strerror))

        # crl
        self.store_crl(profile_nickname, cert, key, crl, crl_valid_for)

    def store_crl(self, profile_nickname, cert, key, crl, crl_valid_for):
        """Stores the CRL in the filestore."""
        path = self._setup_directory("ca", profile_nickname)
        data = crl.export(cert, key, type=crypto.FILETYPE_PEM, days=crl_valid_for, digest="sha256")
        try:
            with open(os.path.join(path, "crl_{}.pem".format(profile_nickname)), "w") as f:
                f.write(data)
                f.write("\n")
        except IOError as exc:
            raise FileStoreError("Error writing crl data: {}".format(exc.strerror))

    def load_ca(self, profile_nickname):
        """Loads the (cert, key, crl) for the given profile_nickname."""
        path = self._cert_path("ca", profile_nickname)

        try:
            # cert
            with open(os.path.join(path, "ca_{}.pem".format(profile_nickname)), "r") as f:
                data = f.read()
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, data)

            # key
            with open(os.path.join(path, "key_{}.pem".format(profile_nickname)), "r") as f:
                data = f.read()
            key = crypto.load_privatekey(crypto.FILETYPE_PEM, data)

            # crl
            with open(os.path.join(path, "crl_{}.pem".format(profile_nickname)), "r") as f:
                data = f.read()
            crl = crypto.load_crl(crypto.FILETYPE_PEM, data)
        except IOError as exc:
            raise FileStoreError("Error loading cert data: {}".format(exc.strerror))

        return (cert, key, crl)

    def store_cert(self, issuer_nickname, cert, key=None):
        """Stores the cert and optionally the key for the given CA issuer_nickname."""
        path = self._setup_directory("cert", issuer_nickname)

        try:
            (cert_pem, key_pem) = x509.export_pem(cert, key)

            # cert
            with open(os.path.join(path, "cert_{}.pem".format(cert.get_serial_number())), "w") as f:
                f.write(cert_pem)
                f.write("\n")

            # key
            if key_pem:
                with open(os.path.join(path, "key_{}.pem".format(cert.get_serial_number())), "w") as f:
                    f.write(key_pem)
                    f.write("\n")
        except IOError as exc:
            raise FileStoreError("Error writing cert data: {}".format(exc.strerror))

    def load_cert(self, cert_filename):
        """Loads a certificate cert at the given filename."""
        try:
            with open(cert_filename) as f:
                data = f.read()
        except IOError as exc:
            raise FileStoreError("Error loading cert data: {}".format(exc.strerror))
        
        try:
            return crypto.load_certificate(crypto.FILETYPE_PEM, data)
        except crypto.Error:
            raise FileStoreError('Invalid certificate')

    def load_request(self, csr_filename):
        """Loads a request (CSR) from the given file."""
        try:
            with open(csr_filename) as f:
                data = f.read()
        except IOError as exc:
            raise FileStoreError("Error reading CSR data: {}".format(exc.strerror))

        try:
            return crypto.load_certificate_request(crypto.FILETYPE_PEM, data)
        except crypto.Error:
            raise FileStoreError('Invalid request file')
