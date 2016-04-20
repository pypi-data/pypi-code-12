from bitarray import bitarray

from .field import FieldWrapper


class BitStream(object):
    """Expected to be subclasses and fields declared on subclasses that define
    in what way should the data be serialized and deserialized.

    Overridable attributes:

    :attr start_marker: A string used to indicate the start of a data record
                        in it's serialized form.
    :attr end_marker:   A string used to indicate the end of a data record
                        in it's serialized form.

    Constructor arguments:

    :param data: it serves multiple purposes:
                 - as a string it represents the data to be deserialized
                 - as an iterable of dicts it's the source data to be
                   serialized
    """
    # Expected to be overridden in subclasses
    start_marker = None
    end_marker = None
    # Internally used attributes
    _pre_processor_prefix = 'preprocess_'
    _post_processor_prefix = 'postprocess_'

    def __init__(self, data):
        self._data = data
        if self.start_marker is None or self.end_marker is None:
            raise TypeError("Both start_marker and end_marker must be defined")
        if len(self.start_marker) != len(self.end_marker):
            raise ValueError("Use markers of equal length.")
        self._fields = self._collect_fields()

    def _collect_fields(self):
        fields = []
        for name in dir(self):
            attr = getattr(self, name)
            if isinstance(attr, FieldWrapper):
                fields.append(attr.instantiate(name))
        return sorted(fields, key=lambda x: x._index)

    def _run_processor(self, prefix, field_name, value):
        processor_name = prefix + field_name
        processor = getattr(self, processor_name, None)
        if callable(processor):
            return processor(value)
        return value

    def _to_datagram(self, data):
        datagram = bitarray()
        datagram.frombytes(self.start_marker)
        for field in self._fields:
            value = self._run_processor(self._pre_processor_prefix,
                                        field.name,
                                        data[field.name])
            datagram = datagram + field.serialize(value)
        datagram.frombytes(self.end_marker)
        return datagram

    def serialize(self):
        """Perform serialization of the data that was passed to the
        constructor and return it in it's serialized form.
        """
        bitstream = bitarray()
        for item in self._data:
            bitstream = bitstream + self._to_datagram(item)
        return bitstream.tobytes()

    def _from_datagram(self, datagram):
        pos = 0
        data = dict()
        for field in self._fields:
            bits = datagram[pos:pos + field.width]
            deserialized = field.deserialize(bits)
            data[field.name] = self._run_processor(self._post_processor_prefix,
                                                   field.name,
                                                   deserialized)
            pos += field.width
        return data

    def deserialize(self):
        """Perform deserialization of the data that was passed to the
        constructor and return it in it's deserialized form.
        """
        bitstream = bitarray()
        bitstream.frombytes(self._data)
        end_pattern = bitarray()
        end_pattern.frombytes(self.end_marker)
        pattern_width = end_pattern.length()
        start = pattern_width
        deserialized = []
        for end in bitstream.itersearch(end_pattern):
            found_start = bitstream[start - pattern_width:start].tobytes()
            if found_start != self.start_marker:
                raise ValueError('Start marker does not match.')
            data = self._from_datagram(bitstream[start:end])
            deserialized.append(data)
            start = end + pattern_width * 2
        return deserialized

    @classmethod
    def to_bytes(cls, raw_data):
        """Helper method to instantiate a class with the passed in
        ``raw_data`` and implicitly call and return the result of it's
        ``serialize`` method.

        :param raw_data: data to be serialized
        """
        instance = cls(raw_data)
        return instance.serialize()

    @classmethod
    def from_bytes(cls, raw_bytes):
        """Helper method to instantiate a class with the passed in
        ``raw_bytes`` and implicitly call and return the result of it's
        ``deserialize`` method.

        :param raw_bytes: data to be deserialized
        """
        instance = cls(raw_bytes)
        return instance.deserialize()
