from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from marshmallow.fields import Field
from pytz import timezone


class LagosTimezone(Field):
    """A formatted datetime/date based on the Lagos timezone.

    Unlike default marshmallow fields it uses `read_only` rather than
    `dump_only` to enable setting default value. When setting `read_only`
    to true it is expected that `missing` will also be passed.
    """
    default_error_messages = {
        'invalid': 'Not a valid datetime.',
        'format': '"{input}" cannot be formatted as a datetime.',
    }
    lagos = timezone('Africa/Lagos')

    def __init__(self, read_only=False, **kwargs):
        super().__init__(**kwargs)
        self.read_only = read_only
        if read_only and not self.missing:  # ignore deserialize if no missing is passed
            self.dump_only = True

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        try:
            value = self.lagos.localize(value)
            return value.strftime(self.dateformat)
        except AttributeError:
            self.fail('format', input=value)

    def _deserialize(self, value, attr, data):
        if self.read_only:  # use missing if read_only
            value = self.missing() if callable(self.missing) else self.missing

        if not value and not self.missing:  # falsy values are invalid
            self.fail('invalid')

        value = self.missing() if not value else value
        try:
            date = datetime.strptime(value, self.dateformat)
            return self.lagos.localize(date)
        except (AttributeError, TypeError, ValueError):
            self.fail('invalid')

    @classmethod
    def now(cls):
        return cls.lagos.localize(datetime.now())


class DateTime(LagosTimezone):
    dateformat = '%Y-%m-%d %H:%M:%S'

    @classmethod
    def now_str(cls):
        return cls.now().strftime(cls.dateformat)


class ObjectID(Field):
    """Serializes and deserializes ObjectId strs from mongodb"""
    default_error_messages = {
        'invalid': 'Not a valid ObjectId.',
        'format': '"{input}" cannot be formatted as an ObjectId.',
    }

    def _serialize(self, value, attr, obj):
        if value is None:
            return None
        elif isinstance(value, ObjectId):
            return str(value)
        else:
            self.fail('format', input=value)

    def _deserialize(self, value, attr, obj):
        if not value:
            self.fail('invalid')
        try:
            return ObjectId(value)
        except InvalidId:
            self.fail('invalid')
