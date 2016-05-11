import re
from django.core import validators
from django.forms import CharField
from django.utils.six import text_type

class RandomStringField(CharField):
    def __init__(self, *args, **kwargs):
        valid_chars = kwargs.pop("valid_chars")
        super(RandomStringField, self).__init__(*args, **kwargs)
        self.validators.append(validators.RegexValidator(regex=text_type("^[%s]+$") % re.escape(valid_chars)))