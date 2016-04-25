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

# flake8: noqa
from .keys import ECKeyFile, RemoteKey
from .request import CertificateRequest
from .acme import ACMEAuthority, UnexpectedHTTPStatus


def get_certificate(account_key, csr, webroot, register=True, no_www=True):
    acme = ACMEAuthority(account_key)
    if register:
        acme.register()

    def make_path(dn):
        if no_www and dn.startswith("www."):
            dn = dn[4:]
        return webroot.format(dn)

    return acme.get_certificate(csr, make_path)
