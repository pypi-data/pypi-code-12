from time import sleep, time
import unittest

from distributed.cluster import Loop
from distributed import Executor
from distributed.utils_test import inc

from distributed.cluster.utils_test import ClusterTest

def test_simple():
    with Loop(4, scheduler_port=0) as c:
        with Executor((c.scheduler.ip, c.scheduler.port)) as e:
            x = e.submit(inc, 1)
            x.result()
            assert x.key in c.scheduler.tasks
            assert any(w.data == {x.key: 2} for w in c.workers)


class LoopTest(ClusterTest, unittest.TestCase):
    Cluster = Loop
