from time import sleep, time
import unittest

from distributed.cluster import SubProcess
from distributed.cluster.utils_test import ClusterTest


class SubProcessTest(ClusterTest, unittest.TestCase):
    Cluster = SubProcess
