from .field import BitField


def register_data_type(data_type, serializer_fn, deserializer_fn):
    """Add a new data serializer and deserializer to all ``BitField`` objects
    (including subclasses as well). This is just a helper function that simply
    delegates calls to the classmethod on ``BitField`` itself.

    :param data_type:       name of the type
    :param serializer_fn:   function that performs serialization
    :param deserializer_fn: function that performs deserialization
    """
    BitField.register_data_type(data_type, serializer_fn, deserializer_fn)
