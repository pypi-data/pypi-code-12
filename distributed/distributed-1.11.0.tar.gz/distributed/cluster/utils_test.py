from __future__ import print_function, division, absolute_import

from ..executor import Executor
from ..utils_test import inc


class ClusterTest(object):
    def setUp(self):
        self.cluster = self.Cluster(4, scheduler_port=0)
        self.executor = Executor((self.cluster.scheduler.ip,
                                  self.cluster.scheduler.port))

    def tearDown(self):
        self.executor.shutdown()
        self.cluster.close()

    def test_computation(self):
        x = self.executor.submit(inc, 1)
        assert x.result() == 2

    def test_ncores(self):
        with self.Cluster(2) as c:
            with Executor((c.scheduler.ip, c.scheduler.port)) as e:
                assert len(e.ncores()) == 2

    def test_start_and_stop_workers(self):
        n = len(self.executor.ncores())
        w = self.cluster.start_worker()
        assert len(self.executor.ncores()) == n + 1
        self.cluster.stop_worker(w)
        assert len(self.executor.ncores()) == n
