"""
This package imports the codecs that can be used for de- and encoding incoming
and outgoing messages:

- :class:`JSON` uses `JSON <http://www.json.org/>`_
- :class:`MsgPack` uses `msgpack <http://msgpack.org/>`_
- :class:`MsgPackBlosc` uses `msgpack <http://msgpack.org/>`_ and
  `Blosc <http://blosc.org/>`_

All codecs should implement the base class :class:`Codec`.

"""
import inspect
import json
import sys

try:
    import blosc
except ImportError:
    blosc = None
try:
    import msgpack
except ImportError:
    msgpack = None

from .exceptions import SerializationError

__all__ = ['serializable', 'Codec', 'JSON', 'MsgPack', 'MsgPackBlosc']


TYPESIZE = 8 if sys.maxsize > 2**32 else 4


def serializable(cls=None, repr=True):
    """Class decorator that makes the decorated class serializable by
    :mod:`aiomas.codecs`.

    The decorator tries to extract all arguments to the class’ ``__init__()``.
    That means, the arguments must be available as attributes with the same
    name.

    The decorator adds the following methods to the decorated class:

    - ``__asdict__()``: Returns a dict with all __init__ parameters

    - ``__fromdict__(dict)``: Creates a new class instance from *dict*

    - ``__serializer__()``: Returns a tuple with args for
      :meth:`Codec.add_serializer()`

    - ``__repr__()``: Returns a generic instance representation.  Adding this
      method can be deactivated by passing ``repr=False`` to the decorator.

    Example:

    .. code-block:: python

        >>> import aiomas.codecs
        >>>
        >>> @aiomas.codecs.serializable
        ... class A:
        ...     def __init__(self, x, y):
        ...         self.x = x
        ...         self._y = y
        ...
        ...     @property
        ...     def y(self):
        ...         return self._y
        >>>
        >>> codec = aiomas.codecs.JSON()
        >>> codec.add_serializer(*A.__serializer__())
        >>> a = codec.decode(codec.encode(A(1, 2)))
        >>> a
        A(x=1, y=2)

    """
    def wrap(cls):
        attrs = [a for a in inspect.signature(cls).parameters]

        def __asdict__(self):
            return {a: getattr(self, a) for a in attrs}

        @classmethod
        def __fromdict__(cls, attrs):
            return cls(**attrs)

        def __repr__(self):
            args = ('%s=%r' % (a, getattr(self, a)) for a in attrs)
            return '%s(%s)' % (self.__class__.__name__, ', '.join(args))

        @classmethod
        def __serializer__(cls):
            return (cls, cls.__asdict__, cls.__fromdict__)

        cls.__asdict__ = __asdict__
        cls.__fromdict__ = __fromdict__
        cls.__serializer__ = __serializer__
        if repr:
            cls.__repr__ = __repr__

        return cls

    # The type of "cls" depends on the usage of the decorator.  It's a class if
    # it's used as `@serializable` but ``None`` if used as `@serializable()`.
    if cls is None:
        return wrap
    else:
        return wrap(cls)


class Codec:
    """Base class for all Codecs.

    Subclasses must implement :meth:`encode()` and :meth:`decode()`.

    """
    def __init__(self):
        self._serializers = {}
        self._deserializers = {}

    def __str__(self):
        return '%s[%s]' % (self.__class__.__name__,
                           ', '.join(s.__name__ for s in self._serializers))

    def encode(self, data):
        """Encode the given *data* and return a :class:`bytes` object."""
        raise NotImplementedError

    def decode(self, data):
        """Decode *data* from :class:`bytes` to the original data structure."""
        raise NotImplementedError

    def add_serializer(self, type, serialize, deserialize):
        """Add methods to *serialize* and *deserialize* objects typed *type*.

        This can be used to de-/encode objects that the codec otherwise
        couldn't encode.

        *serialize* will receive the unencoded object and needs to return
        an encodable serialization of it.

        *deserialize* will receive an objects representation and should return
        an instance of the original object.

        """
        if type in self._serializers:
            raise ValueError('There is already a serializer for type "%s"' %
                             type)
        typeid = len(self._serializers)
        self._serializers[type] = (typeid, serialize)
        self._deserializers[typeid] = deserialize

    def serialize_obj(self, obj):
        """Serialize *obj* to something that the codec can encode."""
        orig_type = otype = type(obj)
        if otype not in self._serializers:
            # Fallback to a generic serializer (if available)
            otype = object

        try:
            typeid, serialize = self._serializers[otype]
        except KeyError:
            raise SerializationError('No serializer found for type "%s"' %
                                     orig_type) from None

        try:
            return {'__type__': (typeid, serialize(obj))}
        except Exception as e:
            raise SerializationError('Could not serialize object "%r": %s' %
                                     (obj, e)) from e

    def deserialize_obj(self, obj_repr):
        """Deserialize the original object from *obj_repr*."""
        # This method is called for *all* dicts so we have to check if it
        # contains a desrializable type.
        if '__type__' in obj_repr:
            typeid, data = obj_repr['__type__']
            obj_repr = self._deserializers[typeid](data)
        return obj_repr


class JSON(Codec):
    """A :class:`Codec` that uses *JSON* to encode and decode messages."""

    def encode(self, data):
        return json.dumps(data, default=self.serialize_obj).encode()

    def decode(self, data):
        return json.loads(data.decode(), object_hook=self.deserialize_obj)


class MsgPack(Codec):
    """A :class:`Codec` that uses *msgpack* to encode and decode messages."""
    def __init__(self):
        if msgpack is None:
            msg = ('Please install "msgpack-python" to use the %s codec: '
                   'pip install -U aiomas[mp]' % self.__class__.__name__)
            raise ImportError(msg)
        super().__init__()

    def encode(self, data):
        return msgpack.packb(
            data, default=self.serialize_obj, use_bin_type=True)

    def decode(self, data):
        return msgpack.unpackb(data,
                               object_hook=self.deserialize_obj,
                               use_list=False,
                               encoding='utf-8')


class MsgPackBlosc(Codec):
    """A :class:`Codec` that uses *msgpack* to encode and decode messages and
    *blosc* to compress them."""
    def __init__(self):
        if msgpack is None or blosc is None:
            msg = ('Please install "msgpack-python" and "blosc" to use the %s '
                   'codec: pip install -U aiomas[mpb]' %
                   self.__class__.__name__)
            raise ImportError(msg)
        super().__init__()

    def encode(self, data):
        return blosc.compress(msgpack.packb(
            data, default=self.serialize_obj, use_bin_type=True), TYPESIZE)

    def decode(self, data):
        return msgpack.unpackb(blosc.decompress(bytes(data)),
                               object_hook=self.deserialize_obj,
                               use_list=False,
                               encoding='utf-8')
