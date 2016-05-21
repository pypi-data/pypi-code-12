"""
 Copyright (C) 2016 Maruf Maniruzzaman
 Website: http://cosmosframework.com
 Author: Maruf Maniruzzaman
 License :: OSI Approved :: MIT License
"""

import OpenSSL.crypto as crypto


# sudo apt-get install build-essential libssl-dev libffi-dev python-dev
# pip install pyOpenSSL


def generate_certificate(key_length, cn, organizational_unit, organization, locality, state_or_province, country):
    request = crypto.X509Req()

    subject = request.get_subject()

    subject.CN = cn
    subject.organizationalUnitName = organizational_unit
    subject.organizationName = organization
    subject.localityName = locality
    subject.stateOrProvinceName = state_or_province
    subject.countryName = country

    key = generate_key(key_length)

    request.set_pubkey(key)
    request.sign(key, "sha256")

    csr = crypto.dump_certificate_request(crypto.FILETYPE_PEM, request)
    private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)

    certificate = {"private_key": private_key, "csr": csr, "key_length": key_length}

    return certificate


def generate_key(key_length):
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, key_length)
    return key


def sign_certificate(req, issuerCert, issuerKey, serial, notBefore, notAfter, digest="md5"):
    """
    Generate a certificate given a certificate request.
    Arguments: req        - Certificate reqeust to use
               issuerCert - The certificate of the issuer
               issuerKey  - The private key of the issuer
               serial     - Serial number for the certificate
               notBefore  - Timestamp (relative to now) when the certificate
                            starts being valid
               notAfter   - Timestamp (relative to now) when the certificate
                            stops being valid
               digest     - Digest method to use for signing, default is md5
    Returns:   The signed certificate in an X509 object
    """

    # from https://github.com/msabramo/pyOpenSSL/blob/master/examples/certgen.py
    # -*- coding: latin-1 -*-
    #
    # Copyright (C) AB Strakt
    # Copyright (C) Jean-Paul Calderone
    # License : Apache 2.0

    cert = crypto.X509()
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(notBefore)
    cert.gmtime_adj_notAfter(notAfter)
    cert.set_issuer(issuerCert.get_subject())
    cert.set_subject(req.get_subject())
    cert.set_pubkey(req.get_pubkey())
    cert.sign(issuerKey, digest)
    return cert