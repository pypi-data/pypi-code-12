import sys
import zsearch_definitions.protocols_pb2

class Abstractocol(object):
    def __init__(self, value, name, pretty_name):
        self.value, self.name, self.pretty_name = value, name, pretty_name

    @classmethod
    def from_value(cls, value):
        return cls._by_value[value]

    @classmethod
    def from_name(cls, name):
        return cls._by_name[name]

    @classmethod
    def from_pretty_name(cls, name):
        return cls._by_pretty_name[name]

    def __hash__(self):
        return self.value.__hash__()

    def __cmp__(self, other):
        return self.value.__cmp__(other.value)


# can't share between classes, so create abstract class with all the methods
# and then maintain your own things in sep children classes

class Subprotocol(Abstractocol):
    _by_pretty_name = {}
    _by_name = {}
    _by_value = {}


class Protocol(Abstractocol):
    _by_pretty_name = {}
    _by_name = {}
    _by_value = {}


for _spid in zsearch_definitions.protocols_pb2.Subprotocol.values():
    enum_name = zsearch_definitions.protocols_pb2.Subprotocol.Name(_spid)
    simple_name = enum_name[len("SUBPROTO_"):]
    pretty_name = simple_name.lower()
    object_ = Subprotocol(_spid, enum_name, pretty_name)
    Subprotocol._by_name[enum_name] = object_
    Subprotocol._by_value[_spid] = object_
    Subprotocol._by_pretty_name[pretty_name] = object_
    setattr(Protocol, simple_name, object_)

for _pid in zsearch_definitions.protocols_pb2.Protocol.values():
    enum_name = zsearch_definitions.protocols_pb2.Protocol.Name(_pid)
    simple_name = enum_name[len("PROTO_"):]
    pretty_name = simple_name.lower()
    object_ = Protocol(_pid, enum_name, pretty_name)
    Protocol._by_name[enum_name] = object_
    Protocol._by_value[_pid] = object_
    Protocol._by_pretty_name[pretty_name] = object_
    setattr(sys.modules[__name__], simple_name, object_)

