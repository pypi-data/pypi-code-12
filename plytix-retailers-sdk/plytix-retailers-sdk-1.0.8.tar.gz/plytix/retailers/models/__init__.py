from plytix.retailers import enum

import sys

PY3 = sys.version_info[0] == 3
if PY3:
    string_type = str
    text_type = str

    def bytes_from_hex(h):
        return bytes.fromhex(h)
else:
    string_type = basestring
    text_type = unicode

    def bytes_from_hex(h):
        return h.decode('hex')


def validate_id(oid):
    if isinstance(oid, string_type):
        if len(oid) == 24:
            try:
                id = bytes_from_hex(oid)
            except (TypeError, ValueError):
                raise ValueError('Invalid ID: {}'.format(oid))
        else:
            raise ValueError('Invalid ID: {}'.format(oid))
    else:
        raise TypeError("The id must be a 12-byte unique identifier.")
    return True


OPERATOR = enum(AND='AND', OR='OR')


class BaseModel(object):

    def __repr__(self):  # pragma: no cover
        class_name = self.__class__.__name__
        return '<{}: {} object>'.format(class_name, class_name)

    def is_valid(self, creating=False):
        """
        :return: True if the model is ready to be saved or updated.
        """
        if not creating and hasattr(self, 'id'):
            if id is not None:
                return validate_id(self.id)
        return True

    def to_dict(self, include_id=True):
        """
        :param include_id: Include ID in the dictionary
        :return: A dictionary for the model.
        """
        raise NotImplementedError # pragma: no cover

    @staticmethod
    def parse(data):
        """
        :param data: Data response.
        :return: An instance of the model from the data.
        """
        raise NotImplementedError # pragma: no cover

