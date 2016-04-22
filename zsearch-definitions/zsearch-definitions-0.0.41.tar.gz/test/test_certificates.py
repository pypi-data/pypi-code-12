import json
import test.testcase
import time
import unittest

from zsearch_definitions import anonstore_pb2


class CertificateTests(test.testcase.ZDBTestCase):

    TIMEOUT = 3

    def setUp(self):
        super(CertificateTests, self).setUp()
        self.service = self.query_grpc.service

    def get_mock_certificates(self):
        certs = json.loads(open("test/certificates.json").read())
        return certs

    def add_mock_certificates(self):
        certs = self.get_mock_certificates()
        for cert in certs:
            self.query_grpc.put_certificate(cert["raw"], cert["parsed"])
        return certs

    def test_add_new_certificates(self):
        certs = self.get_mock_certificates()
        for cert in certs:
            raw = cert["raw"]
            parsed = cert["parsed"]
            delta = self.query_grpc.put_certificate(raw, parsed)
            self.assertEqual(delta.delta_type, anonstore_pb2.AnonymousDelta.DT_UPDATE)
            self.assertEqual(delta.delta_scope, anonstore_pb2.AnonymousDelta.SCOPE_NEW)
            self.assertAnoymousDeltaMatchesCertificate(delta, cert)

    def test_add_repeat_certificates(self):
        certs = self.add_mock_certificates()
        for cert in certs:
            raw = cert["raw"]
            parsed = cert["parsed"]
            delta = self.query_grpc.put_certificate(raw, parsed)
            self.assertEqual(delta.delta_type, anonstore_pb2.AnonymousDelta.DT_UPDATE)
            self.assertEqual(delta.delta_scope, anonstore_pb2.AnonymousDelta.SCOPE_NO_CHANGE)

    def test_certificate_dump(self):
        certs = self.add_mock_certificates()
        original_raw = {c["raw"] for c in certs}
        original_parsed = {json.dumps(c["parsed"], sort_keys=True) for c in certs}
        self.admin_grpc.dump_certificates(path="certificates.json", incremental=False)
        new_raw = set()
        new_parsed = set()
        with open("certificates.json", "r") as fd:
            for line in fd:
                c = json.loads(line)
                raw = c["raw"]
                parsed = c["parsed"]
                new_raw.add(raw)
                new_parsed.add(json.dumps(parsed, sort_keys=True))
        self.assertEqual(original_raw, new_raw)
        self.assertEqual(original_parsed, new_parsed)



if __name__ == "__main__":
    unittest.main()
