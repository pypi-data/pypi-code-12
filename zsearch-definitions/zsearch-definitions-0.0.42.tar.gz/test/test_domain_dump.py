import json
import test.testcase
import time
import json
import os.path
import sys
import unittest

from zsearch_definitions.protocols_pb2 import Protocol, Subprotocol

class TestDomainDumpTestCase(test.testcase.ZDBTestCase):

    TEST_HTTPS_TLS = json.dumps({"tls_enabled":True, "tls_version":"TLSv1.2"}, sort_keys=True)
    TEST_HTTPS_HB = json.dumps({"heartbeat_enabled":True, "heartbleed_vulnerable":False}, sort_keys=True)
    TEST_FTP_BANNER = json.dumps({"banner":"go away drew springall"}, sort_keys=True)

    def add_mock_records(self):
        self.query_grpc.put_host_domain_record("google.com", "141.212.120.5", 443,
                "PROTO_HTTPS",
                "SUBPROTO_TLS",
                self.TEST_HTTPS_TLS,
                tags=["tag_https", "tag_https2"])
        self.query_grpc.put_host_domain_record("google.com", "141.212.120.5", 443,
                "PROTO_HTTPS",
                "SUBPROTO_HEARTBLEED",
                self.TEST_HTTPS_HB)
        self.query_grpc.put_host_domain_record("google.com", "141.212.108.1", 22,
                "PROTO_FTP",
                "SUBPROTO_BANNER",
                self.TEST_FTP_BANNER,
                metadata={"manufacturer":"Google!"})
        self.query_grpc.put_host_domain_record("facebook.com", "141.212.121.1", 22,
                "PROTO_FTP",
                "SUBPROTO_BANNER",
                self.TEST_FTP_BANNER,
                metadata={"manufacturer":"Dell"})

    def parse_domain_json_dump(self, path):
        retv = {}
        with open(path) as fd:
            for line in fd:
                j = json.loads(line.strip())
                retv[j["domain"]] = j
        return retv

    VALID = json.loads("""{"__restricted_location":{"city":"Ann Arbor","continent":"North America","country":"United States","country_code":"US","latitude":42.292299999999997,"longitude":-83.714500000000001,"postal_code":"48109","province":"Michigan","registered_country":"United States","registered_country_code":"US","timezone":"America/Detroit"},"ip":"141.212.121.1","ip_int":2379512065,"location":{"city":"Ann Arbor","continent":"North America","country":"United States","country_code":"US","latitude":42.292299999999997,"longitude":-83.714500000000001,"postal_code":"48109","province":"Michigan","registered_country":"United States","registered_country_code":"US","timezone":"America/Detroit"},"metadata":{"manufacturer":"Dell"},"p22":{"ftp":{"banner":{"banner":"go away drew springall"}}},"p443":{"https":{"heartbleed":{"heartbeat_enabled":true,"heartbleed_vulnerable":false},"tls":{"tls_enabled":true,"tls_version":"TLSv1.2"}}},"tags":["tag_https","tag_https2"]}""")

    def test_json_dumps(self):
        if os.path.exists("domain.json"):
            os.remove("domain.json")
        time.sleep(1)
        self.add_mock_records()
        record_count = 0
        for record in self.query_grpc.iter_domain_records():
            record_count += 1
        self.assertTrue(record_count > 0)
        self.admin_grpc.dump_domain(path="domain.json")
        #self.assertEqual(self.VALID, self.parse_domain_json_dump("domain.json")["google.com"])


if __name__ == "__main__":
    unittest.main()
