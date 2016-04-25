from base64 import b64encode, b64decode
from cPickle import loads, dumps

from django.db import models
from django.core import exceptions

class PickleField(models.TextField):
    __metaclass__=models.SubfieldBase

    magic='PickleFieldv1\n'

    def __init__(self, value_class, *args, **kwargs):
        super(PickleField, self).__init__(*args, **kwargs)
        self.value_class=value_class

    def db_type(self):
        return 'text'

    def to_python(self, value):
        """Because we can't tell the difference between a normal Python string and a
        Python string containing an base64'd pickle, the approach will be to attempt to unpickle the string,
        and assume failure is because the value was already unpickled.

        We also include a magic format header in the hope of slightly decreasing the cost of this test.
        """
        if value.__class__ in [str, unicode] and value.startswith(self.magic):
            try:
                pck=b64decode(value[len(self.magic):])
                return loads(pck)
            except:
                pass

        if value and not isinstance(value, self.value_class):
            raise exceptions.ValidationError, "This value must be an instance of %s."%self.value_class.__name__

        return value

    def get_db_prep_save(self, value):
        return self.magic + b64encode(dumps(value))

    def formfield(self, *args, **kwargs):
        return None
