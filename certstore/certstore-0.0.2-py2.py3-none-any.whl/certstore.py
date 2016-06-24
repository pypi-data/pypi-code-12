# -*- coding: utf-8 -*-
"""Path to system certificate bundle file in `ca_bundle`.

If OS is Windows a tempfile is created.
Otherwise look for existing files on known paths, assume file is a certificate
store.

Note: Assuming located cert stores is based on tecnique used by previous
versions of `pip`. Note that `pip` has abandoned this in versions > 8.1.2, due
to possible issues with broken OpenSSL shipped with OS. This package aim to fit
the "90%" usecase.
"""
import atexit
import os

CA_BUNDLE_PATHS = [
    "/etc/ssl/certs/ca-certificates.crt",  # Debian/Ubuntu/Gentoo etc.
    "/etc/pki/tls/certs/ca-bundle.crt",  # Fedora/RHEL
    "/etc/ssl/ca-bundle.pem",  # OpenSUSE
    "/etc/ssl/cert.pem",  # OpenBSD
    "/usr/local/share/certs/ca-root-nss.crt",  # FreeBSD/DragonFly
    "/usr/local/etc/openssl/cert.pem",  # Homebrew on OSX
]

if os.name == 'nt':
    import wincertstore

    certfile = wincertstore.CertFile()
    certfile.addstore("CA")
    certfile.addstore("ROOT")
    atexit.register(certfile.close)  # cleanup and remove files on shutdown
    ca_bundle = certfile.name
else:
    ca_bundle = next((x for x in CA_BUNDLE_PATHS if os.path.exists(x)), None)
