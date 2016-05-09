#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
from .testcase import TestCase

from pdml2flow.conf import Conf
from pdml2flow.autovivification import AutoVivification
from pdml2flow.flow import Flow

class TestFlow(TestCase):

    def test_get_flow_id(self):
        Conf.FLOW_DEF = [ ['def1'], ['def2'] ]

        frame = AutoVivification({
            'def1': 1,
            'def2': 2,
        })
        self.assertEqual(Flow.get_flow_id(frame), '[1, 2]')

        frame = AutoVivification({
            'def1': 1,
        })
        self.assertEqual(Flow.get_flow_id(frame), '[1, {}]')

        frame = AutoVivification({
            'def3': 3,
        })
        self.assertEqual(Flow.get_flow_id(frame), None)

    def test_not_expired(self):
        frame = AutoVivification({
            'frame': { 'time_epoch': { 'raw' : [123] } }
        })
        flow = Flow(frame)
        self.assertEqual(flow.not_expired(), True)
        Flow.newest_overall_frame_time = 123
        self.assertEqual(flow.not_expired(), True)
        Flow.newest_overall_frame_time = 123 + Conf.FLOW_BUFFER_TIME
        self.assertEqual(flow.not_expired(), False)

if __name__ == '__main__':
    unittest.main()
