"""
This module contains the bitload class which is used to serialize and
deserialize python values.
"""

from collections import OrderedDict, namedtuple

from bitarray import bitarray

from . import utils


LayoutField = namedtuple('LayoutField', ['start', 'end', 'length',
                                         'serializer', 'deserializer'])


class Bitload(object):
    """
    This class returns an object that is used to serialize and deserialize
    python values. The object is instantiated with the bitload description
    and maintains a map of the bitload layout. This map is used by its methods
    to insert or extract regions of the binary data that belong to individual
    fields.

    The bitload layout is accessible through the :py:attr:`~Bitload.layout`
    property, which is an instance of :py:class:`collections.OrderedDict`. The
    keys correspond to field names, and the values are
    :py:class:`~collections.namedtuple` instances with the following
    attributes:

    - ``start``: starting index of the field
    - ``end``: index one after the final index of the field
    - ``length``: length of the field (in bits)
    - ``serializer``: function used for serializing the python value of the
      field
    - ``deserializer``: function used for deserializing the binary data into
      the python value of the field

    These attributes are read-only and cannot be assigned to.

    After the layout is processed, the object's :py:attr:`~Bitload.length`
    property is set to the total length of the bitload.

    .. warning::
        The object's :py:attr:`~Biload.length` property is *not* read-only, but
        you should not try to change its value unless you know exactly what you
        are doing.

    By default, the length of the bitload is automatically padded to whole
    bytes. To disable the padding, we can pass ``autopad=False`` to the
    constructur, in which case the length of the bitload is a simple sum of
    lengths of the fields (incuding 'pad' fields).
    """

    #: List of fields which have corresponding built-in (de)serializers in the
    #: :py:mod:`btl.utils` module.
    BUILTINS = ['int', 'str', 'bytes', 'hex', 'bool']

    def __init__(self, description, autopad=True):
        self.description = description
        self.layout = OrderedDict({})
        self.length = 0
        for field in description:
            name = field[0]
            ftype = field[1]
            if ftype == 'bool':
                length = 1
            else:
                length = field[2]
            if ftype == 'pad':
                # Field type is padding, so we will bail early, but we'll
                # increment the length so the padding is accounted for in the
                # total length.
                self.length += length
                continue
            if ftype in self.BUILTINS:
                serializer = getattr(utils, '{}_to_bita'.format(ftype))
                deserializer = getattr(utils, 'bita_to_{}'.format(ftype))
            else:
                serializer = field[3]
                deserializer = field[4]
            self.layout[name] = LayoutField(
                start=self.length,
                end=self.length + length,
                length=length,
                serializer=serializer,
                deserializer=deserializer)
            self.length += length
        if autopad and self.length % 8:
            self.length += 8 - (self.length % 8)

    def serialize(self, data):
        """
        Return a bytestring containing serialized and packed data. The ``data``
        object must be a dictionary or a dict-like object that implements key
        access.
        """
        b = bitarray(self.length)
        b.setall(0)
        for name, field in self.layout.items():
            start, end, length, serializer, _ = field
            value = data[name]
            serialized = serializer(value)
            serialized = serialized[-length:]  # trim to correct length
            b[start:end] = serialized
        return b.tobytes()

    def deserialize(self, bitload):
        """
        Return a :py:class:`~collections.OrderedDict` object that contains the
        data from the specified bitload. The ``bitload`` argument should be a
        bytestring.

        If the bitload does not have the correct length, a :py:exc:`ValueError`
        exception is raised.
        """
        b = bitarray()
        b.frombytes(bitload)
        if len(b) != self.length:
            raise ValueError('Length mismatch: got {} but expected {}'.format(
                len(b), self.length))
        data = OrderedDict()
        for name, field in self.layout.items():
            start, end, _, _, deserializer = field
            raw = b[start:end]
            data[name] = deserializer(raw)
        return data


def serialize(description, data, autopad=True):
    """
    Return a serialized bytestring using the specified bitload description and
    data. This is a shortcut for instantiating a :py:class:`Bitload` object and
    calling its :py:meth:`~Bitload.serialize` method.

    The ``autopad`` argument can be used to automatically pad the bitload to
    whole bytes.
    """
    return Bitload(description, autopad).serialize(data)


def deserialize(description, bitload, padded=True):
    """
    Return an :py:class:`~collections.OrderedDict` object using the specified
    bitload description and bitload. This is a shortcut for instantiating a
    :py:class:`Bitload` object and calling its :py:meth:`~Bitload.deserialize`
    method.

    The ``padded`` argument is used to specify whether the incoming bitload
    has been padded to whole bytes.
    """
    return Bitload(description, padded).deserialize(bitload)
