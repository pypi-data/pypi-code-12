import zdb
import itertools
from zsearch_definitions import hoststore_pb2, common_pb2, protocols_pb2
from zsearch_definitions.protocols_pb2 import Protocol, Subprotocol
from zsearch_definitions.rpc_pb2 import *
import time
import unittest
import socket


import testcase


class QueryTest(testcase.ZDBTestCase):

    TIMEOUT = 3

    def setUp(self):
        super(QueryTest, self).setUp()
        self.service = self.query_grpc.service

    def test_get_exists(self):
        record = zdb.get_ipv4_record(0x01020304, 443, 80, 5)
        delta = self.service.PutHostIPv4Record(record, self.TIMEOUT)
        self.assertIsNotNone(delta)
        hq = zdb.host_query_from_record(record)
        res = self.service.GetHostIPv4Record(hq, self.TIMEOUT)
        self.assertEqual(HostQueryResponse.SUCCESS, res.status)
        self.assertHostQueryResponseMatchesHostQuery(res, hq)
        self.assertRecordEqual(record, res.record)

    def test_get_nonexistant(self):
        record = zdb.get_ipv4_record(0x01020304, 443, 80, 5)
        hq = zdb.host_query_from_record(record)
        res = self.service.GetHostIPv4Record(hq, self.TIMEOUT)
        self.assertEqual(HostQueryResponse.NO_RECORD, res.status)

    def test_get_deleted(self):
        record = zdb.get_ipv4_record(0x01020304, 443, 80, 5)
        hq = zdb.host_query_from_record(record)
        delta = self.service.PutHostIPv4Record(record, self.TIMEOUT)
        delta = self.service.DelHostIPv4Record(hq, self.TIMEOUT)
        res = self.service.GetHostIPv4Record(hq, self.TIMEOUT)
        self.assertEqual(HostQueryResponse.NO_RECORD, res.status)


if __name__ == "__main__":
    unittest.main()
