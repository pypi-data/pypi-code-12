#!/usr/bin/env python
"""API methods."""
import x509
import conf


# exceptions for doormouse
class DoormouseError(Exception):
    pass


class FileStoreError(DoormouseError):
    pass


class DataStoreError(DoormouseError):
    pass


# main api class
class Doormouse(object):
    def __init__(self, filestore, datastore):
        self.filestore = filestore
        self.datastore = datastore

    def initialize_issuers(self, cnf):
        """Initializes the CA and SubCA certificates."""
        for ca in cnf["ca"]:
            # process ca and add if necessary
            cert = self.datastore.list_certificates(profile_nickname=ca["nickname"])
            if cert:
                (cacert, cakey, cacrl) = self.filestore.load_ca(ca["nickname"])
            else:
                name = x509.Name(ca.get("cn"), ca.get("o"), ca.get("ou"), ca.get("c"), ca.get("st"), ca.get("l"),
                    ca.get("e"))
                (cacert, cakey, cacrl) = x509.create_ca(name, ca["keysize"], ca["validity"])
                self.datastore.add_certificate(ca["nickname"], ca["nickname"], cacert, "active", "ca")
                self.filestore.store_ca(ca["nickname"], cacert, cakey, cacrl, ca["crl_validity"])

            # process sub ca and add if necessary
            if not "subca" in ca:
                continue
            for subca in ca["subca"]:
                cert = self.datastore.list_certificates(profile_nickname=subca["nickname"])
                if not cert:
                    name = x509.Name(subca.get("cn"), subca.get("o"), subca.get("ou"), subca.get("c"), subca.get("st"),
                        subca.get("l"), subca.get("e"))
                    (subcert, subkey, subcrl) = x509.create_subca(cacert, cakey, name, subca["keysize"], subca["validity"])
                    self.datastore.add_certificate(ca["nickname"], subca["nickname"], subcert, "active", "subca")
                    self.filestore.store_ca(subca["nickname"], subcert, subkey, subcrl, subca["crl_validity"])

    def list_certificates(self, cnf, issuer_nickname=None):
        """Returns a list of dictionaries for matching certificates."""
        if issuer_nickname:
            issuer = conf.find_issuer(cnf, issuer_nickname)
            if not issuer:
                raise ValueError("ca or subca profile '{}' not found in the conf file".format(issuer_nickname))
            certs = self.datastore.list_certificates(issuer_nickname=issuer_nickname)
        else:
            certs = self.datastore.list_certificates()

        return certs

    def create_cert(self, cnf, cert_nickname, common_name, alt_names=[]):
        """Creates an certificate and key pair."""
        # find the appropriate configs
        (issuer_cnf, cert_cnf) = conf.find_issuer_cert(cnf, cert_nickname)
        if not cert_cnf:
            raise ValueError("cert profile '{}' not found in the conf file".format(cert_nickname))

        # load the ca cert and key
        try:
            (cacert, cakey, cacrl) = self.filestore.load_ca(issuer_cnf["nickname"])
        except FileStoreError as exc:
            raise ValueError("unable to load ca '{}': {}".format(issuer_cnf["nickname"], exc))

        # create the name for the cert
        name = x509.Name(common_name, cert_cnf.get("o"), cert_cnf.get("ou"), cert_cnf.get("c"),
            cert_cnf.get("st"), cert_cnf.get("l"), cert_cnf.get("e"))
        for altname in alt_names:
            name.add_altname(x509.ALTTYPE_DNSNAME, altname)

        # create the cert and save it
        (cert, key) = x509.create_cert(cacert, cakey, name, cert_cnf["keysize"], cert_cnf["validity"])
        self.filestore.store_cert(issuer_cnf["nickname"], cert, key)
        self.datastore.add_certificate(issuer_cnf["nickname"], cert_cnf["nickname"], cert, "active", "cert")

    def revoke_certificate(self, cnf, serial_number):
        """Revokes a certificate."""
        cert_data = self.datastore.get_certificate(serial_number)
        if not cert_data:
            raise ValueError("serial number '{}' not found".format(serial_number))
        elif cert_data["status"] == "revoked":
            raise ValueError("certificate is already revoked")
        else:
            issuer_nickname = cert_data["issuer_nickname"]
            issuer_data = conf.find_issuer(cnf, issuer_nickname)
            (ca_cert, ca_key, ca_crl) = self.filestore.load_ca(issuer_nickname)
            x509.revoke(ca_crl, "{:x}".format(int(serial_number)))
            self.filestore.store_crl(issuer_nickname, ca_cert, ca_key, ca_crl, issuer_data["crl_validity"])
            self.datastore.revoke_certificate(serial_number)

    def refresh_crl(self, cnf, issuer_nickname=None):
        """Refreshes all CRLs or a specific CRL."""
        if issuer_nickname:
            issuer = conf.find_issuer(cnf, issuer_nickname)
            if not issuer:
                raise ValueError("ca or subca profile '{}' not found in conf file".format(issuer_nickname))
            (ca_cert, ca_key, ca_crl) = self.filestore.load_ca(issuer["nickname"])
            # storing the CRL automatically updates the nextUpdate field
            self.filestore.store_crl(issuer["nickname"], ca_cert, ca_key, ca_crl, issuer["crl_validity"])

        else:
            issuers = conf.find_issuers(cnf)
            for issuer in issuers:
                (ca_cert, ca_key, ca_crl) = self.filestore.load_ca(issuer["nickname"])
                # storing the CRL automatically updates the nextUpdate field
                self.filestore.store_crl(issuer["nickname"], ca_cert, ca_key, ca_crl, issuer["crl_validity"])

    def list_revoked(self, cnf, issuer_nickname=None):
        """Returns a list of all revoked certificates or revoked certificates for a specific issuer."""
        revoked = []
        if issuer_nickname:
            issuer = conf.find_issuer(cnf, issuer_nickname)
            if not issuer:
                raise ValueError("ca or subca profile '{}' not found in conf file".format(issuer_nickname))
            (ca_cert, ca_key, ca_crl) = self.filestore.load_ca(issuer["nickname"])

            # for some reason, a blank crl returns None instead of ()
            crl_revoked_list = ca_crl.get_revoked()
            if crl_revoked_list:
                for rev in crl_revoked_list:
                    revoked.append(rev.get_serial())
        else:
            for issuer in conf.find_issuers(cnf):
                (ca_cert, ca_key, ca_crl) = self.filestore.load_ca(issuer["nickname"])

                # for some reason, a blank crl returns None instead of ()
                crl_revoked_list = ca_crl.get_revoked()
                if crl_revoked_list:
                    for rev in crl_revoked_list:
                        revoked.append(rev.get_serial())

        # get the profile for each serial number and add a row
        data = []
        for rev in revoked:
            serial = "{}".format(int(rev, 16))
            data.append(self.datastore.get_certificate(serial))

        return data

    def sign(self, cnf, cert_nickname, request_filename):
        """Signs a certificate request."""
        # find the issuer
        (issuer, cert_conf) = conf.find_issuer_cert(cnf, cert_nickname)
        if not issuer:
            raise ValueError("cert profile '{}' not found in conf file".format(cert_nickname))
        (ca_cert, ca_key, ca_crl) = self.filestore.load_ca(issuer["nickname"])

        # load the request
        try:
            request = self.filestore.load_request(request_filename)
        except FileStoreError as exc:
            raise ValueError("can not open request file: {}".format(exc))

        # sign it
        cert = x509.sign(ca_cert, ca_key, request, cert_conf["validity"])

        # add it to the datastore and filestore
        self.datastore.add_certificate(issuer["nickname"], cert_conf["nickname"], cert, "active", "cert")
        self.filestore.store_cert(issuer["nickname"], cert)

    def track(self, cnf, request_filename):
        """Tracks an externally signed certificate."""
        # load the certificate
        try:
            cert = self.filestore.load_cert(request_filename)
        except FileStoreError as exc:
            raise ValueError("can not open certificate file: {}".format(exc))

        # add it to the datastore
        self.datastore.add_certificate("__tracked__", "__tracked__", cert, "active", "cert")

    def remove_certificate(self, cnf, serial_number):
        """Removes a certificate from the datastore."""
        cert_data = self.datastore.get_certificate(serial_number)
        if not cert_data:
            raise ValueError("serial number '{}' not found".format(serial_number))
        else:
            self.datastore.remove_certificate(serial_number)

    def list_expiring(self, cnf, days=30):
        """Returns a list of certificates that are expiring."""
        # make a list of expiring certificates
        expiring = []
        for cert in self.datastore.list_certificates():
            cert_days = x509.days_till_expire(cert["not_after"])
            if cert_days <= days:
                cert["days_till_expire"] = cert_days
                expiring.append(cert)
        return expiring
