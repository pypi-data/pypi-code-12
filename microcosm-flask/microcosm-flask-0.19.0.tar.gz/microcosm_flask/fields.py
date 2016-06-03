"""
Custom fields.

"""
from datetime import datetime

from dateutil import parser
from marshmallow.fields import Field, ValidationError


class EnumField(Field):
    """
    Enum valued field.

    Cribbed from [marshmallow_enum](https://github.com/justanr/marshmallow_enum), which
    is not available on PyPi.

    """
    default_error_messages = {
        'by_name': 'Invalid enum member {name}',
        'by_value': 'Invalid enum value {value}'
    }

    def __init__(self, enum, by_value=False, *args, **kwargs):
        self.enum = enum
        self.by_value = by_value
        super(EnumField, self).__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj):
        if value is None:
            return value
        elif self.by_value:
            return value.value
        else:
            return value.name

    def _deserialize(self, value, attr, data):
        if value is None:
            return value
        elif self.by_value:
            return self._deserialize_by_value(value, attr, data)
        else:
            return self._deserialize_by_name(value, attr, data)

    def _deserialize_by_value(self, value, attr, data):
        try:
            return self.enum(value)
        except ValueError:
            try:
                return self.enum(int(value))
            except:
                pass
            self.fail('by_value', value=value)

    def _deserialize_by_name(self, value, attr, data):
        try:
            return getattr(self.enum, value)
        except AttributeError:
            self.fail('by_name', name=value)


class TimestampField(Field):
    """
    Timestamp valued field, as either a unix timestamp (default) or isoformat string.

    """
    EPOCH = datetime(1970, 1, 1)

    def __init__(self, use_isoformat=False, *args, **kwargs):
        self.use_isoformat = use_isoformat
        super(TimestampField, self).__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj):
        """
        Serialize value as a timestamp, either as a Unix timestamp (in float second) or a UTC isoformat string.

        """
        if value is None:
            return None

        if self.use_isoformat:
            return datetime.utcfromtimestamp(value).isoformat()
        else:
            return value

    def _deserialize(self, value, attr, obj):
        """
        Deserialize value as a Unix timestamp (in float seconds).

        Handle both numeric and UTC isoformat strings.

        """
        if value is None:
            return None

        try:
            return float(value)
        except ValueError:
            parsed = parser.parse(value)
            if parsed.tzinfo:
                if parsed.utcoffset().total_seconds():
                    raise ValidationError("Timestamps must be defined in UTC")
                parsed = parsed.replace(tzinfo=None)
            return (parsed - TimestampField.EPOCH).total_seconds()
