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

import re
from .utils import openssl


class CertificateRequest(object):
    def __init__(self, filename):
        self.filename = filename

    def get_domains(self):
        domains = set()
        data = openssl("req", "-in", self.filename,
                       "-noout", "-text").decode("utf-8")

        common_name = re.search(r"Subject:.*? CN=([^\s,;/]+)", data)
        if common_name is not None:
            domains.add(common_name.group(1))

        subject_alt_names = re.search(
            r"X509v3 Subject Alternative Name:\s*\n\s+([^\n]+)\n",
            data, re.MULTILINE | re.DOTALL)
        if subject_alt_names is not None:
            for san in subject_alt_names.group(1).split(", "):
                if san.startswith("DNS:"):
                    domains.add(san[4:])

        return domains

    def as_der(self):
        return openssl("req", "-in", self.filename, "-outform", "DER")
