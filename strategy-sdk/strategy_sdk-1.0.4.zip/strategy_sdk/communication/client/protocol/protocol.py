# encoding: utf-8
import io
import threading

from communication.client.protocol.interface import AbstractFramer
from communication.server import protocol
from communication.server.protocol.protocol import ProtocolMessage
from exception.exception import InvalidRequestRuntimeException
from utils.io.io import DataStream


__author__ = 'Yonka'


class LengthFramer(AbstractFramer):
    def __init__(
            self,
            io_stream: io.RawIOBase,  # as python does not separate input_stream/output_stream interfaces clearly
    ):
        self.ioStream = io_stream
        self.dataStream = DataStream(io_stream, "!")
        self._r_lock = threading.Lock()
        self._w_lock = threading.Lock()

    def next_msg(self) -> ProtocolMessage:
        with self._r_lock:
            fc = self.dataStream.read_int32()  # java readInt
            req_id = self.dataStream.read_int64()  # java readLong
            msg_type = self.dataStream.read_int32()  # java readInt
            body_length = self.dataStream.read_int32()  # java readInt
            if body_length > protocol.MAX_SIZE or body_length < 0:
                raise InvalidRequestRuntimeException("got unexpected body size: %d" % body_length)
            elif req_id < 0 or msg_type < 0 or fc < 0:
                raise InvalidRequestRuntimeException("invalid reqId or msgType or function code")
            body = b""
            while len(body) < body_length:
                body += self.ioStream.read(body_length - len(body))  # type: bytes
            # print("finish msg: %s" % body)
            return ProtocolMessage(fc, req_id, msg_type, body.decode("utf-8"))  # bytes -> str

    def frame_msg(self, message: ProtocolMessage):
        with self._w_lock:
            if message.body is not None and len(message.body.encode("utf-8")) > protocol.MAX_SIZE:
                raise ValueError("invalid message size")
            bs = message.to_stream_bytes('!')
            self.ioStream.write(bs)
            self.ioStream.flush()
