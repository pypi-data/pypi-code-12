# This file is part of le_client.
#
# le_client is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# le_client is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with le_client.  If not, see <http://www.gnu.org/licenses/>.


import argparse
import urllib.parse
import re
import os
import sys

from .request import CertificateRequest
from .keys import ECKeyFile, RemoteKey
from . import get_certificate


def run():
    env_key = os.environ.get("ACME_ACCOUNT_KEY", None)
    prog = sys.argv[0]
    if prog.endswith("__main__.py"):
        prog = "python -m {}".format(__package__)

    parser = argparse.ArgumentParser(description="Obtains a TLS certificate",
                                     prog=prog)

    parser.add_argument(
        "--key", required=env_key is None,
        help="A PEM-encoded file with account private key"
             " or URL of a Chatelain service. If starts with '@' then"
             " it's a path to a one-liner text file that contains such value."
             " Optional if ACME_ACCOUNT_KEY environment variable is present.")

    parser.add_argument(
        "--register", default=False, action="store_true",
        help="Make sure account key is registered.")

    parser.add_argument(
        "--webroot", required=True,
        help="A path template with {} in place of domain name")

    parser.add_argument(
        "--no-www", dest="no_www", default=False, action="store_true",
        help="Strip 'www.' prefix for http-01 webroot path")

    parser.add_argument("--csr", help="CSR file", required=True)

    parser.add_argument(
        "--out",
        help="Output filename. If not specified, certificate will be "
             "written to stdout.")

    args = parser.parse_args()

    if args.key is None:
        args.key = env_key
    if args.key.startswith("@"):
        with open(args.key[1:], "rU") as f:
            args.key = f.readline().strip()
    if re.match("^https?://", args.key):
        url = urllib.parse.urlsplit(args.key)
        if (url.username is not None and url.password is not None):
            credentials = (url.username, url.password)
            url = url._replace(netloc=url.netloc.split("@", 1)[1])
        else:
            credentials = None
        url = urllib.parse.urlunsplit(url)
        key = RemoteKey(url, credentials=credentials)
    else:
        key = ECKeyFile(args.key)

    csr = CertificateRequest(args.csr)
    cert = get_certificate(
        key, csr, args.webroot,
        register=args.register, no_www=args.no_www
    )
    if args.out is not None:
        with open(args.out, "w") as f:
            f.write(cert)
    else:
        print(cert)


if __name__ == "__main__":
    run()
