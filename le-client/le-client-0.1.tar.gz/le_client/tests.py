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


import unittest
from unittest.mock import Mock, patch, call, ANY
import textwrap
import base64
import json

from . import ACMEAuthority, ECKeyFile, CertificateRequest


class LeClientTestCase(unittest.TestCase):
    @patch("subprocess.Popen")
    def test_ec_key(self, popen):
        KEY_DUMP = textwrap.dedent("""
            Private-Key: (256 bit)
            priv:
                04:00:00:00:00:00:00:00:00:00:00:00:00:00:00:
                00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:
                00:01
            pub:
                04:00:00:00:00:00:00:00:00:00:00:00:00:00:00:
                00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:
                00:00:01:00:00:00:00:00:00:00:00:00:00:00:00:
                00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:
                00:00:00:00:02
            ASN1 OID: prime256v1
            NIST CURVE: P-256
        """).strip().encode("ascii")

        def mock_openssl(*whatever):
            return (KEY_DUMP, "wat")

        process = Mock()
        process.communicate = Mock(return_value=mock_openssl())
        process.returncode = 0
        popen.return_value = process

        key = ECKeyFile("mock.pem")
        jwk = key.as_jwk()
        self.assertEquals(jwk, {
            "kty": "EC",
            "crv": "P-256",
            "x": "A" * 42 + "E",
            "y": "A" * 42 + "I",
        })

    @patch("subprocess.Popen")
    def test_csr(self, popen):
        CSR_DUMP = textwrap.dedent("""
            Certificate Request:
                Data:
                    Version: 0 (0x0)
                    Subject:
                    Subject Public Key Info:
                        Public Key Algorithm: id-ecPublicKey
                            Public-Key: (256 bit)
                            pub:
                                [skipped]
                            ASN1 OID: prime256v1
                            NIST CURVE: P-256
                    Attributes:
                    Requested Extensions:
                        X509v3 Subject Alternative Name:
                            DNS:example.org, DNS:www.example.org
                Signature Algorithm: ecdsa-with-SHA256
                     [skipped]
        """).strip().encode("ascii")

        def mock_openssl(*whatever):
            return (CSR_DUMP, "wat")

        process = Mock()
        process.communicate = Mock(return_value=mock_openssl())
        process.returncode = 0
        popen.return_value = process

        csr = CertificateRequest("mock.csr")
        domains = csr.get_domains()
        self.assertEquals(domains, {"example.org", "www.example.org"})

    @patch("urllib.request.urlopen")
    def test_registration(self, urlopen):
        key = Mock()
        key.sign = Mock(return_value="MockSignature")

        def mock_urlopen(url, data=None):
            headers = {"Replay-Nonce": "MockNonce"}
            response = Mock()
            response.status = 200
            if url.endswith("/new-reg"):
                headers["Location"] = "mock://reg-location"
                response.status = 201
            response.headers = headers
            response.read = Mock(return_value=b'{"mock": true}')
            return response
        urlopen.side_effect = mock_urlopen

        acme = ACMEAuthority(key, base_url="mock://base")
        is_new, location = acme.register()

        urlopen.assert_has_calls([
            call(acme.base_url + "/directory", None),
            call(acme.base_url + "/acme/new-reg", b'"MockSignature"')
        ])
        self.assertTrue(is_new)
        self.assertEquals(location, "mock://reg-location")

    @patch("builtins.open")
    @patch("urllib.request.urlopen")
    def test_challenge(self, urlopen, fileopen):
        key = Mock()
        key.sign = Mock(return_value="MockSignature")

        challenge_counter = [0]

        def mock_urlopen(url, data=None):
            headers = {"Replay-Nonce": "MockNonce"}
            response = Mock()
            if url.endswith("/new-authz"):
                response.status = 201
                response.read = Mock(return_value=json.dumps({
                    "status": "pending",
                    "challenges": [
                        {
                            "status": "pending",
                            "type": "some-unknown-type-01",
                            "uri": "mock://challenge/wrong-one",
                            "token": "whatever",
                        },
                        {
                            "status": "pending",
                            "type": "http-01",
                            "uri": "mock://challenge/http-01",
                            "token": "mock-token-01",
                        },
                    ],
                    "combinations": [[0], [1]],
                }).encode("utf-8"))
            elif url.endswith("/challenge/http-01"):
                response.status = 202
                c = b'pending' if challenge_counter[0] < 2 else b'valid'
                response.read = Mock(return_value=b'{"status": "' + c + b'"}')
                challenge_counter[0] += 1
            elif url.endswith("/new-cert"):
                response.status = 201
                response.read = Mock(return_value=b'MockCertificateBlob')
            else:
                response.status = 200
                response.read = Mock(return_value=b'{}')
            response.headers = headers
            return response
        urlopen.side_effect = mock_urlopen

        csr = Mock()
        csr.get_domains = Mock(return_value={"example.org"})
        csr.as_der = Mock(return_value=b'MockCSRDERData')
        path_maker = Mock(return_value="/tmp/mock/path")

        acme = ACMEAuthority(key, base_url="mock://base")
        with patch("time.sleep") as sleep:
            certificate = acme.get_certificate(csr, path_maker)
            sleep.assert_has_calls([call(ANY)])

        path_maker.assert_has_calls([call("example.org")])
        fileopen.assert_has_calls([call("/tmp/mock/path/mock-token-01", "w")])

        self.assertEqual(
            certificate,
            "\n".join([
                "-----BEGIN CERTIFICATE-----",
                base64.b64encode(b'MockCertificateBlob').decode("ascii"),
                "-----END CERTIFICATE-----", ""
            ])
        )


if __name__ == "__main__":
    unittest.main()
