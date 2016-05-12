# encoding: utf-8
from __future__ import absolute_import
from communication.server.protocol import function_code
from communication.server.protocol.protocol import ProtocolMessage

__author__ = u'Yonka'

HEADER_SIZE = 20
CLIENT_ID_SIZE = 4
REQID_SIZE = 4
PC_SIZE = 4
LEN_SIZE = 4
MAX_SIZE = 15000000

hb = ProtocolMessage(function_code.HEARTBEAT, 0, function_code.STRATEGY, u"")
hb_ack = ProtocolMessage(function_code.ACK, 0, function_code.STRATEGY, u"")


def new_strategy_hb_msg():
    return hb


def new_strategy_hb_ack_msg():
    return hb_ack
