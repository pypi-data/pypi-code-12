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
import urllib.error
import base64
import json
import re
import collections
import os
import time
import textwrap

from .utils import b64, first


Response = collections.namedtuple("Response", "status headers data")


class UnexpectedHTTPStatus(RuntimeError):
    def __init__(self, status):
        super(UnexpectedHTTPStatus, self).__init__(
            "Unexpected HTTP status code: {}".format(status)
        )


class ACMEChallenge(object):
    def __init__(self, data):
        self.challenge_data = data
        self.challenge_type = data["type"]
        self.uri = data["uri"]
        self.status = data["status"]

    def __getattr__(self, name):
        if name in self.challenge_data:
            return self.challenge_data[name]
        else:
            raise AttributeError(
                "Challenge doesn't have attribute {}".format(name))


class ACMEChallengeSet(frozenset):
    def __new__(cls, challenges):
        return super(ACMEChallengeSet, cls).__new__(cls, challenges)

    @property
    def types(self):
        return set(c.challenge_type for c in self)


class ACMEChallenges(frozenset):
    def __new__(cls, challenge_sets):
        return super(ACMEChallenges, cls).__new__(cls, challenge_sets)

    def find(self, *known_types):
        known_types_set = set(known_types)
        for challenge_set in self:
            if challenge_set.types <= known_types_set:
                yield challenge_set


class ACMEAuthority(object):
    PRODUCTION_BASE_URL = "https://acme-v01.api.letsencrypt.org"
    STAGING_BASE_URL = "https://acme-staging.api.letsencrypt.org"
    AGREEMENT_URL = ("https://letsencrypt.org/documents"
                     "/LE-SA-v1.0.1-July-27-2015.pdf")
    DEFAULT_BASE_URL = PRODUCTION_BASE_URL

    def __init__(self, account_key, base_url=None):
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.account_key = account_key
        self._nonce = None

    def get_nonce(self, force_new=False):
        if self._nonce is None or force_new:
            self._nonce = None
            if self.request("/directory").status != 200:
                raise RuntimeError("Failed to obtain Replay-Nonce: HTTP error")
            if self._nonce is None:
                raise RuntimeError("Failed to obtain Replay-Nonce: no header")
        nonce = self._nonce
        self._nonce = None   # This nonce is no more. It ceased to be.
        return nonce

    def request(self, url, payload=None, raw=False):
        if url.startswith("https://"):
            full_url = url
        else:
            full_url = "{}{}".format(self.base_url, url)
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
        else:
            data = None

        try:
            res = urllib.request.urlopen(full_url, data)
        except urllib.error.HTTPError as e:
            res = e

        new_nonce = res.headers.get("Replay-Nonce", None)
        if new_nonce is not None:
            self._nonce = new_nonce

        data = res.read()
        if not raw:
            data = json.loads(data.decode("utf-8"))
        if hasattr(res, "close"):
            res.close()
        return Response(res.status, res.headers, data)

    def request_signed(self, url, payload, raw=False):
        nonce = self.get_nonce()
        signed_payload = self.account_key.sign(nonce, payload)
        return self.request(url, signed_payload, raw=raw)

    def register(self):
        res = self.request_signed("/acme/new-reg", {
            "resource": "new-reg",
            "agreement": self.AGREEMENT_URL,
        })
        if res.status not in (201, 409):
            raise UnexpectedHTTPStatus(res.status)
        return res.status == 201, res.headers.get("Location", None)

    def authorize(self, domain):
        res = self.request_signed("/acme/new-authz", {
            "resource": "new-authz",
            "identifier": {"type": "dns", "value": domain}
        })
        if res.status != 201:
            raise UnexpectedHTTPStatus(res.status)
        data = res.data

        challenges = [ACMEChallenge(c) for c in data["challenges"]]
        combinations = ACMEChallenges(
            ACMEChallengeSet([challenges[n] for n in combination])
            for combination in data.get("combinations", [])
        )
        return data, combinations

    def check_challenge(self, challenge):
        return self.request(challenge.uri)

    def authorize_http01(self, challenge, path, wait=True):
        token = re.sub(r"[^A-Za-z0-9_\-]", "_", challenge.token)
        thumbprint = self.account_key.thumbprint()
        authorization = "{0}.{1}".format(token, thumbprint)
        with open(os.path.join(path, challenge.token), "w") as f:
            f.write(authorization)

        res = self.request_signed(challenge.uri, {
            "resource": "challenge",
            "keyAuthorization": authorization,
        })
        if res.status != 202:
            raise UnexpectedHTTPStatus(res.status)

        if wait:
            while True:
                data = self.check_challenge(challenge).data
                status = data["status"]
                if status == "valid":
                    return True
                elif status == "pending":
                    time.sleep(2)
                else:
                    raise RuntimeError("Challenge failed: {}".format(status))
        else:
            return res

    def request_certificate(self, csr):
        res = self.request_signed("/acme/new-cert", {
            "resource": "new-cert",
            "csr": b64(csr.as_der())
        }, raw=True)
        if res.status != 201:
            raise UnexpectedHTTPStatus(res.status)

        return ("-----BEGIN CERTIFICATE-----\n"
                "{}\n"
                "-----END CERTIFICATE-----\n").format(
            "\n".join(
                textwrap.wrap(base64.b64encode(res.data).decode("ascii"), 64)
            )
        )

    def get_certificate(self, csr, http01_path_func):
        for domain in csr.get_domains():
            data, challenges = self.authorize(domain)
            if data["status"] == "pending":
                challenge_set = first(challenges.find("http-01"))
                for challenge in challenge_set:
                    self.authorize_http01(challenge, http01_path_func(domain))
        return self.request_certificate(csr)
