from django.db import models
from django.core.exceptions import ValidationError
import json
import datetime
from django.utils.translation import ugettext_lazy as _
from widgets import LODWidget


# Serialize datetime which may be present in the JSON
json.JSONEncoder.default = lambda self, obj: (obj.isoformat() if
    isinstance(obj, datetime.datetime) else None)


def validate_object(value, fields):
    """
    Validate the Python object and
    raise errors in case of invalid
    keys in the list of dictionaries
    """
    for i, val in enumerate(value):
        val_keys = val.keys()

        # Check if the keys are Valid
        for k in val_keys:
            if k not in fields:
                raise ValidationError(_("Invalid Key: %s in index: %d" % (str(k), i)))

        # Check if a key is missing
        for f in fields:
            if f not in val_keys:
                raise ValidationError(_("Key: %s is missing in index: %d" % (f, i)))
    return False


class LODField(models.Field):
    """
    A Model field to represent a List of
    Python Dictionaries
    """
    description = "List of Python Dictionaries"

    def __init__(self, *args, **kwargs):
        """
        Initialize
            :fields - A list of Key names
            :lines - Max number of Dictionaries (Djago Admin)
            :max_length - Size of underlying VARCHAR
        """
        self.fields = kwargs.pop('keys', ["Key", "Value"])
        self.lines = kwargs.pop('lines', 10)
        self.char_size = kwargs.pop('max_length', 1000000)

        if type(self.fields) != list:
            raise ValidationError(_("Invalid value: fields"))

        if type(self.char_size) != int:
            raise ValidationError(_("Invalid value: char_size"))

        if type(self.lines) != int:
            raise ValidationError(_("Invalid value: lines"))

        if any([type(k) != str for k in self.fields]):
            raise ValidationError(_("All Keys should be string"))

        super(LODField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        """ Deconstructor function """
        name, path, args, kwargs = super(LODField,
            self).deconstruct()
        return name, path, args, kwargs

    def db_type(self, connection):
        """ Underlying SQL Column type """
        return 'VARCHAR(%s)' % self.char_size

    def from_db_value(self, value, expression, connection, context):
        """ Convert data from DB """
        return self.to_python(value=value)

    def get_prep_value(self, value):
        """ Prepare object to be saved to DB """
        validate_object(value=value, fields=self.fields)
        return json.dumps(value or [])

    def to_python(self, value):
        """ Convert to Python Object """
        return json.loads(value or '[]')

    def pre_save(self, model_instance, add):
        """ Convert to Saved format """
        value = getattr(model_instance, self.attname)
        value = self.to_python(value=json.dumps(value or []))
        setattr(model_instance, self.attname, value)
        return value

    def formfield(self, **kwargs):
        """ Set the custom form widget for this field """
        kwargs['widget'] = LODWidget(keys=self.fields,
            lines=self.lines)
        return super(LODField, self).formfield(**kwargs)
