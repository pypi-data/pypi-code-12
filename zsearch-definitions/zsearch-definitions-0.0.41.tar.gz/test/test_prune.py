import zdb
import itertools
from zsearch_definitions import hoststore_pb2, common_pb2, rpc_pb2, protocols_pb2
from zsearch_definitions.protocols_pb2 import Protocol, Subprotocol
import time
import unittest
import socket
import struct



import testcase


class PruneTest(testcase.ZDBTestCase):

    TIMEOUT = 3

    MIN_HTTPS_TLS_SCAN_ID = 4
    MIN_HTTP_GET_SCAN_ID = 8

    MIN_SCAN_IDS = [
        (443, protocols_pb2.PROTO_HTTPS, protocols_pb2.SUBPROTO_TLS, MIN_HTTPS_TLS_SCAN_ID),
        (80, protocols_pb2.PROTO_HTTP, protocols_pb2.SUBPROTO_GET, MIN_HTTP_GET_SCAN_ID),
    ]

    IPV4_DELTA_QUEUE = "ipv4_deltas"
    DOMAIN_DELTA_QUEUE = "domain_deltas"

    def setUp(self):
        super(PruneTest, self).setUp()
        self.rctx = self.c.redis
        self.admin_service = self.admin_grpc.service
        self.query_service = self.query_grpc.service
        self.rctx.delete(self.IPV4_DELTA_QUEUE)
        self.rctx.delete(self.DOMAIN_DELTA_QUEUE)

    def make_prune_command(self, min_scan_ids):
        cmd = rpc_pb2.Command()
        for port, protocol, subprotocol, min_scan_id in min_scan_ids:
            network_port = self.htons(port)
            ak = hoststore_pb2.AnonymousKey(port=network_port, protocol=protocol,
                                            subprotocol=subprotocol)
            min_id = cmd.min_scan_ids.add()
            min_id.key.CopyFrom(ak)
            min_id.min_scan_id = min_scan_id
        return cmd

    def add_mock_ipv4(self):
        pass

    def test_prune_empty(self):
        cmd = self.make_prune_command(self.MIN_SCAN_IDS)
        res = self.admin_service.PruneIPv4(cmd, self.TIMEOUT)
        self.assertEqual(res.status, rpc_pb2.CommandReply.SUCCESS)

    def test_prune_one_protocol(self):
        records = list()
        for scan_id in range(0,10):
            ip = 0x010203 + scan_id
            record = zdb.get_ipv4_record(
                ip, 443,
                protocols_pb2.PROTO_HTTPS, protocols_pb2.SUBPROTO_TLS,
                scan_id=scan_id
            )
            records.append(record)
        for record in records:
            delta = self.query_service.PutHostIPv4Record(record, self.TIMEOUT)
            self.assertDeltaMatchesRecords(delta, [record])
        cmd = self.make_prune_command(self.MIN_SCAN_IDS)
        res = self.admin_service.PruneIPv4(cmd, self.TIMEOUT)
        self.assertEqual(res.status, rpc_pb2.CommandReply.SUCCESS)
        for record in records:
            hq = zdb.host_query_from_record(record)
            res = self.query_service.GetHostIPv4Record(hq, self.TIMEOUT)
            if record.scanid < self.MIN_HTTPS_TLS_SCAN_ID:
                self.assertEqual(res.status, rpc_pb2.HostQueryResponse.NO_RECORD)
            else:
                self.assertEqual(res.status, rpc_pb2.HostQueryResponse.SUCCESS)
                self.assertRecordEqual(record, res.record)

    def test_prune_many_protocols(self):
        https_records = list()
        http_records = list()
        other_records = list()
        scan_ids = reversed(range(1, 20, 3))
        start_ip = 0x8945ebc6
        ips = range(start_ip, start_ip + 10)
        for sid, ip in itertools.izip(scan_ids, ips):
            https_record = zdb.get_ipv4_record(
                ip, 443,
                protocols_pb2.PROTO_HTTPS, protocols_pb2.SUBPROTO_TLS,
                scan_id=sid,
            )
            http_record = zdb.get_ipv4_record(
                ip, 80,
                protocols_pb2.PROTO_HTTP, protocols_pb2.SUBPROTO_GET,
                scan_id=sid+1,
            )
            other = zdb.get_ipv4_record(
                ip, 443,
                protocols_pb2.PROTO_HTTPS, protocols_pb2.SUBPROTO_GET,
                scan_id=sid+2,
            )
            https_records.append(https_record)
            http_records.append(http_record)
            other_records.append(other)
        for record in itertools.chain(
                https_records, http_records, other_records):
            delta = self.query_service.PutHostIPv4Record(record, self.TIMEOUT)
            self.assertDeltaContainsRecord(delta, record)
        self.rctx.delete(self.IPV4_DELTA_QUEUE)
        cmd = self.make_prune_command(self.MIN_SCAN_IDS)
        res = self.admin_service.PruneIPv4(cmd, self.TIMEOUT)
        self.assertEqual(rpc_pb2.CommandReply.SUCCESS, res.status)
        pruned_records = list()
        for https in https_records:
            hq = zdb.host_query_from_record(https)
            res = self.query_service.GetHostIPv4Record(hq, self.TIMEOUT)
            if https.scanid < self.MIN_HTTPS_TLS_SCAN_ID:
                self.assertEqual(res.status, rpc_pb2.HostQueryResponse.NO_RECORD)
                pruned_records.append(https)
            else:
                self.assertEqual(res.status, rpc_pb2.HostQueryResponse.SUCCESS)
                self.assertRecordEqual(https, res.record)
        for http in http_records:
            hq = zdb.host_query_from_record(http)
            res = self.query_service.GetHostIPv4Record(hq, self.TIMEOUT)
            if http.scanid < self.MIN_HTTP_GET_SCAN_ID:
                self.assertEqual(res.status, rpc_pb2.HostQueryResponse.NO_RECORD)
                pruned_records.append(http)
            else:
                self.assertEqual(res.status, rpc_pb2.HostQueryResponse.SUCCESS)
                self.assertRecordEqual(http, res.record)
        for other in other_records:
            hq = zdb.host_query_from_record(other)
            res = self.query_service.GetHostIPv4Record(hq, self.TIMEOUT)
            self.assertEqual(res.status, rpc_pb2.HostQueryResponse.SUCCESS)
            self.assertRecordEqual(other, res.record)
        expected_deltas = len(pruned_records)
        self.assertTrue(expected_deltas > 0)
        deltas = list()
        for idx in range(0, expected_deltas):
            raw_delta = self.rctx.blpop(self.IPV4_DELTA_QUEUE, timeout=3)
            self.assertIsNotNone(raw_delta)
            self.assertEqual(2, len(raw_delta))
            delta = hoststore_pb2.Delta()
            delta.ParseFromString(raw_delta[1])
            deltas.append(delta)
        delta_queue_len = self.rctx.llen(self.IPV4_DELTA_QUEUE)
        self.assertEqual(0, delta_queue_len)
        for delta in deltas:
            self.assertEqual(delta.delta_type, common_pb2.DT_DELETE)

    def test_prune_domain(self):
        domains = ["a.com", "b.com", "c.com", "google.com"]
        scan_ids = range(1,10)
        records = list()
        for domain, sid in itertools.izip(domains, scan_ids):
            record = zdb.get_domain_record(
                domain, 443,
                protocols_pb2.PROTO_HTTPS, protocols_pb2.SUBPROTO_TLS,
                scan_id=sid,
            )
            self.query_service.PutHostDomainRecord(record, self.TIMEOUT)
            records.append(record)
        self.rctx.delete(self.DOMAIN_DELTA_QUEUE)
        cmd = self.make_prune_command(self.MIN_SCAN_IDS)
        prune_result = self.admin_service.PruneDomain(cmd, self.TIMEOUT)
        self.assertEqual(rpc_pb2.CommandReply.SUCCESS, prune_result.status)
        pruned_records = list()
        for record in records:
            hq = zdb.host_query_from_record(record)
            res = self.query_service.GetHostDomainRecord(hq, self.TIMEOUT)
            if record.scanid < self.MIN_HTTPS_TLS_SCAN_ID:
                self.assertEqual(rpc_pb2.HostQueryResponse.NO_RECORD, res.status)
                pruned_records.append(record)
            else:
                self.assertEqual(rpc_pb2.CommandReply.SUCCESS, res.status)
                self.assertRecordEqual(record, res.record)
        delta_len = self.rctx.llen(self.DOMAIN_DELTA_QUEUE)
        self.assertEqual(len(pruned_records), delta_len)
        for record in pruned_records:
            raw_delta = self.rctx.blpop(self.DOMAIN_DELTA_QUEUE)
            self.assertEqual(2, len(raw_delta))
            delta = hoststore_pb2.Delta()
            delta.ParseFromString(raw_delta[1])
            self.assertEqual(delta.delta_type, common_pb2.DT_DELETE)

    def test_cannot_prune_version(self):
        min_ids = [
            (25, protocols_pb2.PROTO_HTTPS, protocols_pb2.SUBPROTO_SYS_VERSION, 20),
        ]
        cmd = self.make_prune_command(min_ids)
        res = self.admin_service.PruneIPv4(cmd, self.TIMEOUT)
        self.assertEqual(res.status, rpc_pb2.CommandReply.ERROR)
        res = self.admin_service.PruneDomain(cmd, self.TIMEOUT)
        self.assertEqual(res.status, rpc_pb2.CommandReply.ERROR)

    def test_regenerate_deltas_ipv4(self):
        https_records = list()
        http_records = list()
        other_records = list()
        scan_ids = reversed(range(1, 20, 3))
        start_ip = 0x8945ebc6
        ips = range(start_ip, start_ip + 10)
        ip_set = set()
        for sid, ip in itertools.izip(scan_ids, ips):
            ip_set.add(ip)
            https_record = zdb.get_ipv4_record(
                ip, 443,
                protocols_pb2.PROTO_HTTPS, protocols_pb2.SUBPROTO_TLS,
                scan_id=sid,
            )
            http_record = zdb.get_ipv4_record(
                ip, 80,
                protocols_pb2.PROTO_HTTP, protocols_pb2.SUBPROTO_GET,
                scan_id=sid+1,
            )
            other = zdb.get_ipv4_record(
                ip, 443,
                protocols_pb2.PROTO_HTTPS, protocols_pb2.SUBPROTO_GET,
                scan_id=sid+2,
            )
            https_records.append(https_record)
            http_records.append(http_record)
            other_records.append(other)
        for record in itertools.chain(
                https_records, http_records, other_records):
            delta = self.query_service.PutHostIPv4Record(record, self.TIMEOUT)
            self.assertDeltaContainsRecord(delta, record)
        self.rctx.delete(self.IPV4_DELTA_QUEUE)
        cmd = rpc_pb2.Command()
        cmd.start_ip = 0
        cmd.stop_ip = socket.htonl(1000000)
        res = self.admin_service.RegenerateIPv4Deltas(cmd, self.TIMEOUT)
        self.assertEqual(rpc_pb2.CommandReply.SUCCESS, res.status)
        self.assertEqual(0, self.rctx.llen(self.IPV4_DELTA_QUEUE))
        cmd.stop_ip = 0xFFFFFFFF
        res = self.admin_service.RegenerateIPv4Deltas(cmd, self.TIMEOUT)
        self.assertEqual(rpc_pb2.CommandReply.SUCCESS, res.status)
        deltas = list()
        expected_deltas = len(ip_set)
        delta_ips = set()
        for idx in range(0, expected_deltas):
            raw_delta = self.rctx.blpop(self.IPV4_DELTA_QUEUE, timeout=3)
            if raw_delta is None:
                print idx
            self.assertIsNotNone(raw_delta)
            self.assertEqual(2, len(raw_delta))
            delta = hoststore_pb2.Delta()
            delta.ParseFromString(raw_delta[1])
            deltas.append(delta)
            self.assertDeltaVersionMatchesMaxRecord(delta)
            delta_ips.add(socket.ntohl(delta.ip))
            self.assertEqual(5, len(delta.records))
            for record in delta.records:
                self.assertEqual(delta.ip, record.ip)
        self.assertEqual(ip_set, delta_ips)
        delta_queue_len = self.rctx.llen(self.IPV4_DELTA_QUEUE)
        self.assertEqual(0, delta_queue_len)
        self.assertEqual(expected_deltas, len(deltas))

    def test_regenerate_deltas_domain(self):
        https_records = list()
        http_records = list()
        other_records = list()
        scan_ids = reversed(range(1, 20, 3))
        domains = [
            "a.com",
            "b.com",
            "c.com",
            "google.com",
            "f.com",
            "e.com",
            "q.com",
            "z.com",
            "facebook.com",
            "davidadrian.org",
        ]
        domain_set = set()
        for sid, domain in itertools.izip(scan_ids, domains):
            domain_set.add(domain)
            print domain
            https_record = zdb.get_domain_record(
                domain, 443,
                protocols_pb2.PROTO_HTTPS, protocols_pb2.SUBPROTO_TLS,
                scan_id=sid,
            )
            http_record = zdb.get_domain_record(
                domain, 80,
                protocols_pb2.PROTO_HTTP, protocols_pb2.SUBPROTO_GET,
                scan_id=sid+1,
            )
            other = zdb.get_domain_record(
                domain, 443,
                protocols_pb2.PROTO_HTTPS, protocols_pb2.SUBPROTO_GET,
                scan_id=sid+2,
            )
            https_records.append(https_record)
            http_records.append(http_record)
            other_records.append(other)
        for record in itertools.chain(
                https_records, http_records, other_records):
            delta = self.query_service.PutHostDomainRecord(record, self.TIMEOUT)
            self.assertDeltaContainsRecord(delta, record)
        self.rctx.delete(self.DOMAIN_DELTA_QUEUE)
        cmd = rpc_pb2.Command()
        cmd.start_ip = 0
        cmd.stop_ip = socket.htonl(1000000)
        res = self.admin_service.RegenerateDomainDeltas(cmd, self.TIMEOUT)
        self.assertEqual(rpc_pb2.CommandReply.SUCCESS, res.status)
        deltas = list()
        expected_deltas = len(domain_set)
        delta_domains = set()
        for idx in range(0, expected_deltas):
            raw_delta = self.rctx.blpop(self.DOMAIN_DELTA_QUEUE, timeout=3)
            if raw_delta is None:
                print idx
            self.assertIsNotNone(raw_delta)
            self.assertEqual(2, len(raw_delta))
            delta = hoststore_pb2.Delta()
            delta.ParseFromString(raw_delta[1])
            deltas.append(delta)
            self.assertDeltaVersionMatchesMaxRecord(delta)
            delta_domains.add(delta.domain)
            self.assertEqual(5, len(delta.records))
            print delta
            for record in delta.records:
                self.assertEqual(delta.domain, record.domain)
        self.assertEqual(domain_set, delta_domains)
        delta_queue_len = self.rctx.llen(self.DOMAIN_DELTA_QUEUE)
        self.assertEqual(0, delta_queue_len)
        self.assertEqual(expected_deltas, len(deltas))


if __name__ == "__main__":
    unittest.main()
