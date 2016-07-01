#!/bin/env python
# -*- coding: utf-8 -*-

import unittest
from sh import ifconfig

from dockerfly.dockernet.veth import MacvlanEth
from dockerfly.settings import TEST_MOTHER_ETH_NAME

class TestMacvlan(unittest.TestCase):

    def setUp(self):
        self._veth_name = 'testMacvlan'
        self._ip_mask = '192.168.16.10/24'
        self._macvlan = MacvlanEth(self._veth_name, self._ip_mask, TEST_MOTHER_ETH_NAME)

    def test_create_delete_macvlan(self):
        self._macvlan.create()
        self.assertTrue(self._veth_name in ifconfig('-a'))

        self._macvlan.delete()
        self.assertFalse(self._veth_name in ifconfig('-a'))

    def tearDown(self):
        if 'testMacvlan' in ifconfig('-a'):
            self._macvlan.delete()

