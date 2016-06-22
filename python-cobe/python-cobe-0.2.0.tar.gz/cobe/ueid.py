"""Implementation of Unique Entity Identifiers."""

import decimal
import enum
import hashlib
import string

import cobe.model


# Decimal context used for encoding numeric types.
_DECIMAL_CONTEXT = decimal.Context(
    prec=64,
    rounding=decimal.ROUND_HALF_EVEN,
    capitals=False,
    clamp=1,
    Emin=decimal.MIN_EMIN,
    Emax=decimal.MAX_EMAX,
    flags=[],
    traps=[],
)


class UEIDError(Exception):
    """Exception raised for all UEID-related errors."""


class _Type(enum.IntEnum):
    """Enummuration of all value type identifiers."""

    nil = 0x00
    bool = 0x01
    number = 0x02
    unicode = 0x04
    bytes = 0x08
    mapping = 0x10
    array = 0x20


class UEID:
    """Unique Entity Identifier.

    A UEID is used to uniquely identify an entity within a topological model.
    Each UEID combines the *type* and so-called *identifying attributes* of
    the entity. Fundamentally, UEIDs are 32 character long Unicode strings
    containing hexadecimal digits.

    Generally you should use the :meth:`from_attributes` or helper methods
    :meth:`cobe.Update.ueid` and :meth:`cobe.Identifier.ueid` to generate
    a UEID instead directly instantiating this class.

    Instances of this class may be used in a :class:`cobe.Model` in
    order to represent a relationship to a foreign entity. However, note
    that it strongly advised that :class:`cobe.Identifier` be used
    instead, which will handle generation of an accurate UEID itself.

    :param ueid: The UEID as a 32 character string of hexadecimal digits.
    :type ueid: str or cobe.UEID

    :raises UEIDError: If the given UEID is of the wrong type, length or
        contains invalid characters.
    """

    def __init__(self, ueid):
        if isinstance(ueid, UEID):
            ueid = str(ueid)
        if not isinstance(ueid, str):
            raise UEIDError(
                'Excepted type str or UEID, but got {}'.format(type(ueid)))
        if len(ueid) != 32:
            raise UEIDError('Excepted string of length 32; '
                            'but got {} instead'.format(len(ueid)))
        ueid = ueid.lower()
        for character in ueid:
            if character not in string.hexdigits[:-len('ABCDEF')]:
                raise UEIDError(
                    'UEID contains invalid character {!r}'.format(character))
        self._ueid = ueid

    def __str__(self):
        return str(self._ueid)

    def __hash__(self):
        return hash(self._ueid)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._ueid == str(other)

    @classmethod
    def _encode_value(cls, value):
        """Encode value of an arbitrary type.

        :returns: A byte-string containing the encoded value prefixed by
            the value's type identifier.

        :raises TypeError: If the value's type is not encodable.
        """
        try:
            type_, encoder = {
                type(None): (_Type.nil, cls._encode_nil),
                bool: (_Type.bool, cls._encode_bool),
                int: (_Type.number, cls._encode_number),
                float: (_Type.number, cls._encode_number),
                str: (_Type.unicode, cls._encode_unicode),
                bytes: (_Type.bytes, cls._encode_bytes),
                list: (_Type.array, cls._encode_array),
                dict: (_Type.mapping, cls._encode_mapping),
                UEID: (_Type.unicode,
                       lambda ueid: cls._encode_unicode(str(ueid)))
            }[type(value)]
        except KeyError:
            raise TypeError(
                'Cannot encode value of type {!r}'.format(type(value)))
        return bytes([type_]) + encoder(value)

    @staticmethod
    def _encode_nil(nil):
        """Encode a null value."""
        return b''

    @staticmethod
    def _encode_bool(bool_):
        """Encode a boolean value.

        True values because ``0x01`` and false ``0x00``.
        """
        return b'\x01' if bool_ else b'\x00'

    @classmethod
    def _encode_number(cls, number):
        """Encode a numeric value.

        Numbers are converted to Unicode strings encoded as UTF-8 with a
        length prefix. The string representation will always include 64
        digits in the fractional part.
        """
        decimal_ = _DECIMAL_CONTEXT.create_decimal(number)
        return cls._encode_unicode(format(decimal_, '+.64f'))

    @classmethod
    def _encode_unicode(cls, unicode_):
        """Encode a Unicode string.

        The given string is encoded as UTF-8 and prefixed with the length
        of the encoded string which it self is encoded as an integer.
        """
        encoded = unicode_.encode('utf-8')
        return cls._encode_integer(len(encoded)) + encoded

    @classmethod
    def _encode_bytes(cls, bytes_):
        """Encode a byte string.

        This merely prefixes the given byte string with its length encoded
        as an integer.
        """
        return cls._encode_integer(len(bytes_)) + bytes_

    @classmethod
    def _encode_mapping(cls, mapping):
        """Encode and hash an iterable of key-value pairs.

        First the key and value for each pair is encoded. The pairs are then
        sorted by the encoded key's byte value in an ascending fashion. Once
        sorted the encoded pairs are concatenated and hashed with MD5.

        :raises TypeError: If any key or value in the mapping cannot be
            encoded. See :meth:`_encode_value`.
        """
        hash_ = hashlib.md5()
        encoded_pairs = []
        for key, value in mapping.items():
            encoded_pairs.append(
                (cls._encode_value(key), cls._encode_value(value)))
        encoded_pairs.sort(key=lambda pair: pair[0])
        for encoded_key, encoded_value in encoded_pairs:
            hash_.update(encoded_key)
            hash_.update(encoded_value)
        return hash_.digest()

    @classmethod
    def _encode_array(cls, array):
        """Encode an array as if it were a mapping.

        The indicies for the array are encoded as usigned, big-endian
        integers before being used as keys to their corresponding value for
        encoding as a collection.

        :raises TypeError: If any of the values in the array cannot be
            encoded. See :meth:`_encode_value`.
        """
        return cls._encode_mapping(dict(enumerate(array)))

    @staticmethod
    def _encode_integer(integer):
        """Encode integer as bytes.

        The sign of the given integer is ignored and only the minimum number
        of bytes needed to represent the value are used.
        """
        magnitude = abs(integer)
        bits = magnitude.bit_length() if magnitude else 8
        remainder = bits % 8
        if remainder != 0:
            bits = (bits + 8) - remainder
        return magnitude.to_bytes(bits // 8, 'big')

    @classmethod
    def from_attributes(cls, type_, attributes):
        """Generate a UEID from an entity type and attributes.

        This will calculate the UEID from the given identifying attributes
        and entity type.

        :param type_: The type of the entity to generate a UEID for.
        :type type_: str
        :param attributes: The collection of attributes to use to generate
            the UEID. Only those which are identifying attributes will be used.
        :type attributes: cobe.Attributes

        :returns: A new :class:`UEID` generated from the given type and
            attributes.

        :raises UEIDError: If the given entity type or attributes are the
            wrong type, or the UEID cannot be generated for any reason.
        """
        if not isinstance(type_, str):
            raise UEIDError('Excepted type str for entity '
                            'type, but got {}'.format(type(type_)))
        if not isinstance(attributes, cobe.model.Attributes):
            raise UEIDError('Excepted type cobe.Attributes for '
                            'attributes, but got {}'.format(type(attributes)))
        identifying_attributes = {}
        for name in attributes:
            if attributes[name].is_identifier() and attributes[name].is_set():
                identifying_attributes[name] = attributes[name].value
        try:
            ueid_bytes = cls._encode_array([type_, identifying_attributes])
        except TypeError as exc:
            raise UEIDError(str(exc)) from exc
        ueid_hex = ''.join(hex(byte)[2:].zfill(2) for byte in ueid_bytes)
        return cls(ueid_hex)
