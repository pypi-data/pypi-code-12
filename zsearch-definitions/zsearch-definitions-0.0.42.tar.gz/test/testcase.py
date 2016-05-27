import base64
import json
import itertools
import unittest
import time
import socket
import struct

import sh

import zdb

import zsearch_definitions.query
import zsearch_definitions.admin

from zsearch_definitions import common_pb2


class ZDBTestCase(unittest.TestCase):

    @staticmethod
    def deltaKeyMatchesRecord(d, r):
        if a.ip != r.ip:
            return False
        if d.domain != r.domain:
            return False
        return True

    @staticmethod
    def recordsMatch(a, b):
        if a.ip != b.ip:
            return False
        if a.domain != b.domain:
            return False
        if a.port != b.port:
            return False
        if a.protocol != b.protocol:
            return False
        if a.subprotocol != b.subprotocol:
            return False
        return True

    @classmethod
    def setUpClass(cls):
        cls.c = zdb.get_zdb_test_config()

    def setUp(self):
        pkill = sh.Command("pkill")
        try:
            pkill("-9", "zdb")
        except sh.ErrorReturnCode:
            pass
        sh.rm("-rf", sh.glob("/tmp/zdb/*"))
        self.zdb_handle = self.c.zdb(_bg=True, _err="zdb_stderr.txt")
        time.sleep(3)

        self.query_grpc = zsearch_definitions.query.QueryService()
        self.admin_grpc = zsearch_definitions.admin.AdminService()
        self._max_version = 0

    def tearDown(self):
        if self.zdb_handle is not None:
            self.zdb_handle.terminate()

    def assertTagsEqual(self, a, b):
        self.assertEqual(len(a), len(b))
        for atag, btag in itertools.izip(a, b):
            self.assertEqual(atag, btag)

    def assertMetadatumEqual(self, a, b):
        self.assertEqual(a.key, b.key)
        self.assertEqual(a.value, b.value)

    def assertMetadataEqual(self, a, b):
        self.assertEqual(len(a), len(b))
        for am, bm in itertools.izip(a, b):
            self.assertMetadatumEqual(am, bm)

    def assertProtocolAtomEqual(self, a, b):
        # Check data
        self.assertEqual(a.data, b.data)

        # Check tags
        if a.tags is None:
            self.assertIsNone(b.tags)
        else:
            self.assertIsNotNone(b.tags)
            self.assertTagsEqual(a.tags, b.tags)

        # Check metadata
        if a.metadata is None:
            self.assertIsNone(b.metadata)
        else:
            self.assertIsNotNone(b.metadata)
            self.assertMetadataEqual(a.metadata, b.metadata)

    def assertRecordEqual(self, a, b,
                          check_scan_id=True, check_timestamp=True,
                          check_first_seen_at=True, check_last_seen_at=True):
        self.assertEqual(a.ip, b.ip)
        self.assertEqual(a.port, b.port)
        self.assertEqual(a.protocol, b.protocol)
        self.assertEqual(a.subprotocol, b.subprotocol)
        self.assertEqual(a.domain, b.domain)
        self.assertEqual(a.scanid, b.scanid)
        if check_timestamp:
            self.assertEqual(a.timestamp, b.timestamp)
        if check_scan_id:
            self.assertEqual(a.scanid, b.scanid)
        self.assertEqual(a.sha256fp, b.sha256fp)
        if check_first_seen_at:
            self.assertEqual(a.first_seen_at_scan_id, b.first_seen_at_scan_id)
        if check_last_seen_at:
            self.assertEqual(a.last_seen_at_scan_id, b.last_seen_at_scan_id)
        self.assertEqual(a.HasField("atom"), b.HasField("atom"))
        if a.HasField("atom"):
            self.assertProtocolAtomEqual(a.atom, b.atom)
        else:
            # Not yet implemented
            self.fail()

    def assertDeltaVersionMatchesMaxRecord(self, delta):
        self.assertTrue(delta.version > 0)
        for record in delta.records:
            self.assertTrue(record.version <= delta.version)

    def assertDeltaMatchesRecords(self, delta, records):
        delta_records = delta.records
        self.assertTrue(delta.version > 0)
        atom_records = filter(lambda x: x.HasField("atom"), delta_records)
        self.assertEqual(len(atom_records), len(records))
        for record in records:
            self.assertEqual(delta.ip, record.ip)
            self.assertEqual(delta.domain, record.domain)
            found = [
                dr for dr in delta_records
                if ZDBTestCase.recordsMatch(dr, record)
            ]
            self.assertEqual(1, len(found))
            delta_record = found[0]
            self.assertRecordEqual(record, delta_record)
        max_delta_record_version = 0
        for record in delta.records:
            if record.version > max_delta_record_version:
                max_delta_record_version = record.version
        self.assertEqual(max_delta_record_version, delta.version)
        self.assertTrue(delta.version > 0)

    def assertDeltaContainsRecord(self, delta, record):
        delta_records = delta.records
        found = [
            dr for dr in delta_records
            if ZDBTestCase.recordsMatch(dr, record)
        ]
        self.assertEqual(1, len(found))
        self.assertRecordEqual(record, found[0])

    def assertDeltaMatchesHostQuery(self, delta, host_query):
        self.assertEqual(delta.ip, host_query.ip)
        self.assertEqual(delta.domain, host_query.domain)


    def assertAnonymousDeltaMatchesRecord(self, delta, record):
        # unimplemented
        self.fail()

    def assertAnoymousDeltaMatchesCertificate(self, delta, certificate):
        record = delta.record
        self.assertIsNotNone(record)
        self.assertAnonymousRecordMatchesCertificate(record, certificate)

    def assertHostQueryResponseMatchesHostQuery(self, res, query):
        self.assertEqual(query.ip, res.ip)
        self.assertEqual(query.port, res.port)
        self.assertEqual(query.protocol, res.protocol)
        self.assertEqual(query.subprotocol , res.subprotocol)
        self.assertEqual(query.domain, res.domain)

    def assertAnonymousRecordMatchesCertificate(self, record, certificate):
        raw = certificate["raw"]
        parsed = certificate["parsed"]
        self.assertIsNotNone(record)
        self.assertTrue(record.HasField("certificate"))
        rc = record.certificate
        self.assertIsNotNone(rc)
        self.assertEqual(raw, base64.b64encode(rc.raw))
        cert_json = json.dumps(parsed, sort_keys=True)
        self.assertEqual(cert_json, rc.parsed)
        sha1fp = parsed["fingerprint_sha1"].decode("hex")
        sha256fp = parsed["fingerprint_sha256"].decode("hex")
        self.assertEqual(sha1fp, rc.sha1fp)
        self.assertEqual(sha256fp, rc.sha256fp)
        self.assertEqual(sha256fp, record.sha256fp)


    def makeTwoSetOfRecordsWithDifferentTagsAndMetdata(
            self, start_ip, stop_ip,
            first_port, first_protocol, first_subprotocol,
            second_port, second_protocol, second_subprotocol):
        first_tags = ["a", "b"]
        second_tags = ["b", "c"]
        first_metadata = [
            common_pb2.Metadatum(key="k1", value="v1"),
            common_pb2.Metadatum(key="k2", value="v2"),
            common_pb2.Metadatum(key="k3", value="v1"),
        ]
        second_metadata = [
            common_pb2.Metadatum(key="k2", value="a"),
            common_pb2.Metadatum(key="k3", value="b"),
            common_pb2.Metadatum(key="k4", value="c"),
        ]
        first_atoms = zdb.iter_protocol_atom(
            tags_list=itertools.cycle([first_tags]),
            metadata_list=itertools.cycle([first_metadata]),
        )
        second_atoms = zdb.iter_protocol_atom(
            tags_list=itertools.cycle([second_tags]),
            metadata_list=itertools.cycle([second_metadata]),
        )
        first_records = list(zdb.iter_ipv4_record(
                start_ip, first_port, first_protocol, first_subprotocol,
                ip_stop=stop_ip, ip_step=1, atom_list=first_atoms,
        ))
        second_records = list(zdb.iter_ipv4_record(
                start_ip, second_port, second_protocol, second_subprotocol,
                ip_stop=stop_ip, ip_step=1, atom_list=second_atoms,
        ))
        return first_records, second_records

    def htons(self, short):
        short_bytes = struct.pack("!H", short)
        (network_short, ) = struct.unpack("H", short_bytes)
        return network_short
