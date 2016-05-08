# encoding: utf-8
import struct
import unittest

from communication.server.protocol import function_code
from communication.server.protocol.interface import AbstractProtocolMessage


__author__ = 'Yonka'


class ProtocolMessage(AbstractProtocolMessage):
    def __init__(
            self,
            fc: int=0,
            req_id: int=0,
            data_type: int=0,
            body: str=None
    ):
        self.fc = fc
        self.reqId = req_id
        self.dataType = data_type
        self.body = body

    # use struct pack instead of convert_int_to_byte_array and etc, according to java code, we use little endian here
    def to_stream_bytes(self, endian: str="") -> bytes:
        if endian is None:
            endian = ""
        res = b""
        if self.fc >= 0 and self.reqId >= 0 and self.dataType >= 0:
            body_len, body_bs = 0, None
            if self.body is not None:
                body_bs = self.body.encode("utf-8")
                body_len = len(body_bs)
            if body_len == 0:
                res = struct.pack(endian + "lqll", self.fc, self.reqId, self.dataType, 0)
            else:
                res = struct.pack(endian + "lqll%ds" % body_len, self.fc, self.reqId, self.dataType, body_len, body_bs)
        return res

    def is_hb_message(self) -> bool:
        return self.fc == function_code.HEARTBEAT

    def is_ack_message(self) -> bool:
        return self.fc == function_code.ACK

    def __str__(self):
        return "ProtocolMessage(fc: %d, reqId: %d, dataType: %d, body: %s)" % (
            self.fc, self.reqId, self.dataType, self.body)


class TestProtocolMessage(unittest.TestCase):
    def test_to_stream_bytes(self):
        msg1 = ProtocolMessage(1, 1, 1, "123")
        msg2 = ProtocolMessage(1, 1, 1, "")
        msg3 = ProtocolMessage(-1, 1, 1, "123213")
        try:
            assert msg1.to_stream_bytes() == b"\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00" \
                                             b"\x03\x00\x00\x00123"
        except AssertionError as e:
            print("msg1.to_stream_bytes(): %s" % msg1.to_stream_bytes())
            raise e
        try:
            assert msg2.to_stream_bytes() == b"\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00" \
                                             b"\x00\x00\x00\x00"
        except AssertionError as e:
            print("msg2.to_stream_bytes(): %s" % msg2.to_stream_bytes())
            raise e
        try:
            assert msg3.to_stream_bytes() == b""
        except AssertionError as e:
            print("msg3.to_stream_bytes(): %s" % msg3.to_stream_bytes())
            raise e
