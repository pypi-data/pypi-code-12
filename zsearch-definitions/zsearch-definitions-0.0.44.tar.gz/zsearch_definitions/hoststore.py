import socket
import struct
import hashlib
import json

import dateutil.parser
import dateutil.tz
import time

import zsearch_definitions.common_pb2
import zsearch_definitions.hoststore_pb2

class Metadatum(object):

    def __init__(self, key, value):
        self._pb = zsearch_definitions.common_pb2.Metadatum()
        self._pb.key = key
        self._pb.value = value

    @property
    def key(self):
        return self._pb.key

    @property
    def value(self):
        return self._pb.value

    @classmethod
    def from_dict(cls, d):
        '''Turns a dictionary into a list of Metadatum objects'''
        g = [cls(key, value) for key, value in d.iteritems()]
        return g

    @property
    def protobuf(self):
        return self._pb


class ProtocolAtom(object):

    def __init__(self, tags=None, metadata=None, data=None):

        self._pb = zsearch_definitions.hoststore_pb2.ProtocolAtom()

        # Tags
        if tags is None:
            tags = list()
        self._pb.tags.extend(sorted(tags))

        # Globals / values
        if metadata is None:
            metadata = list()
        self._metadata = sorted(metadata, key=lambda m: m.key)

        # Data
        self._data = data or {}
        self._pb.data = json.dumps(self.data, sort_keys=True)

    @property
    def metadata(self):
        return self._metadata

    @property
    def tags(self):
        return self._pb.tags

    @property
    def data(self):
        return self._data

    @property
    def protobuf(self):
        del self._pb.metadata[:]
        self._pb.metadata.extend([x.protobuf for x in self.metadata])
        return self._pb

    def calculate_sha256fp(self, serialized=None):
        if serialized is not None:
            b = serialized
        else:
            b = self.protobuf.SerializeToString()
        m = hashlib.sha1()
        m.update(b)
        return m.digest()


class Record(object):

    def __init__(self, ip, port, protocol, subprotocol,
                 domain=None, timestamp=None, protocol_atom=None,
                 scan_id=None, sha256fp=None):
        if ip is None or port is None or protocol is None or \
                subprotocol is None or protocol_atom is None or \
                scan_id is None or timestamp is None:
            raise Exception("Missing parameter")
        self._pb = zsearch_definitions.hoststore_pb2.Record()
        self._ip = ip
        self._pb.port = port
        self._pb.protocol = protocol
        self._pb.subprotocol = subprotocol
        self._pb.scanid = scan_id
        self._protocol_atom = protocol_atom

        # Set optional members
        if domain is not None:
            self._pb.domain = domain
        self._pb.sha256fp = sha256fp or protocol_atom.calculate_sha256fp()

        # We store IPs in network order whenever they're integers
        ip_bytes = socket.inet_aton(self._ip)
        (ip_net, ) = struct.unpack("I", ip_bytes)
        self._pb.ip = ip_net

        # Convert the time to an int
        dt = dateutil.parser.parse(timestamp).astimezone(dateutil.tz.tzutc())
        self._pb.timestamp = int(time.mktime(dt.timetuple()))

        # Set the protobuf atom, etc.
        self._pb.atom.CopyFrom(protocol_atom.protobuf)

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._pb.port

    @property
    def protocol(self):
        return self._protocol

    @property
    def subprotocol(self):
        return self._subprotocol

    @property
    def atom(self):
        return self._atom

    @property
    def scan_id(self):
        return self._pb.scanid

    @property
    def sha256fp(self):
        return self._pb.sha256fp

    @property
    def timestamp(self):
        return self._pb.timestamp

    @property
    def protobuf(self):
        return self._pb

