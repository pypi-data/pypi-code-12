from bitarray import bitarray

from .utils import pack, unpack, bytes_to_hex, hex_to_bytes


class FieldWrapper(object):
    """Utility class that is used to capture declared fields, preserve their
    order and constructor arguments and later instantiate them when requested.
    """
    _index = 0

    def __init__(self, cls, args, kwargs):
        # to preserve order of declaration
        self._index = FieldWrapper._index
        FieldWrapper._index += 1
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def instantiate(self, name):
        return self.cls(name=name,
                        index=self._index,
                        *self.args,
                        **self.kwargs)


class BitField(object):
    """A class representing a single field within a ``BitStream``. It handles
    the serialization / deserialization of the values / data that is passed
    to it. The following constructor parameters are available:

    :param name:      the name of the field as it was declared
    :param index:     integer, used to keep the order of fields as declared
    :param width:     integer, the needed bit-width for the data
    :param data_type: unique identifier of the data type for which there
                      exists a registered serializer / deserializer
    """
    _serializers = {
        'integer': lambda x: pack('>i', x),
        'float': lambda x: pack('>f', x),
        'hex': lambda x: hex_to_bytes(x),
        'string': lambda x: x,
    }
    _deserializers = {
        'integer': lambda x: unpack('>i', x),
        'float': lambda x: unpack('>f', x),
        'hex': lambda x: bytes_to_hex(x),
        'string': lambda x: x,
    }

    def __new__(cls, *args, **kwargs):
        if 'name' in kwargs:
            return super(BitField, cls).__new__(cls)
        return FieldWrapper(cls, args, kwargs)

    def __init__(self, name, index, width, data_type):
        self._name = name
        self._index = index
        self._width = width
        self._data_type = data_type

    @property
    def width(self):
        """Returns the bit-width of the field that was specified in the field
        declaration."""
        return self._width

    @property
    def data_type(self):
        """Returns the data type of the field that was specified in the field
        declaration."""
        return self._data_type

    @property
    def name(self):
        """Returns the name of the field by which it was declared on the
        ``BitStream`` class."""
        return self._name

    def serialize(self, value):
        """Perform serialization of the passed in value and return it in it's
        serialized form.

        :param value: value to be serialized
        """
        b = bitarray()
        try:
            fn = self._serializers[self.data_type]
        except KeyError:
            raise ValueError('Unknown data_type: {}'.format(self.data_type))
        else:
            b.frombytes(fn(value))
            # cut off unused bits
            return b[b.length() - self.width:]

    def deserialize(self, bits):
        """Perform deserialization of the passed in data and return it in it's
        deserialized form.

        :param bits: data to be deserialized
        """
        bits.reverse()
        bits.fill()
        bits.reverse()
        raw = bits.tobytes()
        try:
            fn = self._deserializers[self.data_type]
        except KeyError:
            raise ValueError('Unknown data_type: {}'.format(self.data_type))
        else:
            return fn(raw)

    @classmethod
    def register_data_type(cls, data_type, serializer_fn, deserializer_fn):
        """Add a new data serializer and deserializer to all ``BitField``
        objects (including subclasses as well).

        :param data_type:       name of the type
        :param serializer_fn:   function that performs serialization
        :param deserializer_fn: function that performs deserialization
        """
        cls._serializers[data_type] = serializer_fn
        cls._deserializers[data_type] = deserializer_fn
