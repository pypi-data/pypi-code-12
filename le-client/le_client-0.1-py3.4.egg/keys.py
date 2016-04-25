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

import urllib.request
import urllib.parse
import urllib.error
import hashlib
import binascii
import json
import re
import abc

from .utils import openssl, b64


class KeyFile(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def as_jwk(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def sign(self, nonce, payload):
        raise NotImplementedError()

    def thumbprint(self):
        jwk_json = json.dumps(self.as_jwk(), sort_keys=True,
                              separators=(",", ":"))
        return b64(hashlib.sha256(jwk_json.encode("utf8")).digest())


class LocalKeyFile(KeyFile, metaclass=abc.ABCMeta):
    def __init__(self, filename):
        self.filename = filename

    @abc.abstractproperty
    def alg(self):
        raise NotImplementedError()

    def sign(self, nonce, payload):
        jwk = self.as_jwk()
        payload64 = b64(json.dumps(payload).encode("utf8"))
        protected64 = b64(json.dumps({
            "alg": self.alg,
            "jwk": jwk,
            "nonce": nonce
        }).encode("utf-8"))

        data = "{}.{}".format(protected64, payload64).encode("ascii")
        out = openssl("dgst", "-sha256", "-sign", self.filename, stdin=data)
        out = out[4:4 + out[3]][-32:] + \
            out[4 + out[3] + 2:4 + out[3] + 3 + out[4 + out[3] + 1]][-32:]

        return {
            "protected": protected64,
            "payload": payload64,
            "signature": b64(out),
        }


class ECKeyFile(LocalKeyFile):
    @property
    def alg(self):
        return "ES256"

    def as_jwk(self):
        dump = openssl("ec", "-in", self.filename,
                       "-noout", "-text").decode("utf-8")
        pub_hex = binascii.unhexlify(re.sub(r"(\s|:)", "", re.search(
            r"pub:\s*\n\s+04:([a-f0-9\:\s]+?)\nASN1 OID: prime256v1\n",
            dump, re.MULTILINE | re.DOTALL).group(1)))
        return {
            "kty": "EC",
            "crv": "P-256",
            "x": b64(pub_hex[:32]),
            "y": b64(pub_hex[32:])
        }


class RemoteKey(KeyFile):
    def __init__(self, url, credentials=None, handlers=None, opener=None):
        self.url = url
        if opener is not None:
            if credentials is not None or handlers is not None:
                raise ValueError("Can't use `opener` with other kwargs")
            self.opener = opener
        else:
            all_handlers = []
            if handlers is not None:
                for handler in handlers:
                    all_handlers.append(handler)
            if credentials is not None:
                passwords = urllib.request.HTTPPasswordMgrWithDefaultRealm()
                passwords.add_password(None, url, *credentials)
                auth_handler = urllib.request.HTTPBasicAuthHandler(passwords)
                all_handlers.append(auth_handler)
            self.opener = urllib.request.build_opener(*all_handlers)

    def as_jwk(self):
        with self.opener.open(self.url) as f:
            assert f.status == 200
            return json.loads(f.read().decode("utf-8"))

    def sign(self, nonce, payload):
        data = json.dumps(payload).encode("utf-8")
        url = "{}?nonce={}".format(self.url, urllib.parse.quote(nonce))
        with self.opener.open(url, data) as f:
            assert f.status == 200
            return json.loads(f.read().decode("utf-8"))
