from __future__ import unicode_literals
from __future__ import print_function
import unittest
from ...sensor_events import ServerAgentPackagesEvent
#from ... import tcell_agent
import json
from ...api import SetEncoder

class MaxLengthTest(unittest.TestCase):
    def test_package_event_create(self):
        sape = ServerAgentPackagesEvent()
        sape.add_package("test_package", "t"*400)
        x = json.loads(json.dumps(sape, cls=SetEncoder))
        self.assertEqual(x["packages"][0]["v"],"t"*256)

