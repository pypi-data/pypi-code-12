import zdb
import itertools
from zsearch_definitions import hoststore_pb2, common_pb2
import time
import unittest

import testcase


# pylint: disable=no-member
class RedisTest(testcase.ZDBTestCase):

    IN_QUEUE = "ipv4"
    DELTA_QUEUE = "ipv4_deltas"

    def setUp(self):
        super(RedisTest, self).setUp()
        self.rctx = self.c.redis
        self.rctx.delete(RedisTest.IN_QUEUE)
        self.rctx.delete(RedisTest.DELTA_QUEUE)

    def test_add_ten_ipv4(self):
        start_ip = 0x01020304
        stop_ip = start_ip + 10
        inc = list(zdb.iter_ipv4_record(start_ip, 443, 3, 2, ip_stop=stop_ip))
        self.assertEqual(len(inc), 10)
        deltas = list()
        for record in inc:
            self.rctx.rpush(RedisTest.IN_QUEUE, record.SerializeToString())
            out = self.rctx.blpop(RedisTest.DELTA_QUEUE, timeout=3)
            self.assertIsNotNone(out)
            self.assertEqual(len(out), 2)
            delta = hoststore_pb2.Delta()
            delta.ParseFromString(out[1])
            deltas.append(delta)
        queue_len = self.rctx.llen(RedisTest.IN_QUEUE)
        self.assertEqual(queue_len, 0)
        for record, delta in itertools.izip(inc, deltas):
            self.assertEqual(delta.delta_type, common_pb2.DT_UPDATE)
            self.assertDeltaMatchesRecords(delta, [record])
        for record in inc:
            self.rctx.rpush(RedisTest.IN_QUEUE, record.SerializeToString())
        # zdb has a 3 second poll
        time.sleep(3)
        delta_len = self.rctx.llen(RedisTest.DELTA_QUEUE)
        self.assertEqual(delta_len, 0)

if __name__ == "__main__":
    unittest.main()
