from django.core import checks, validators
from django.db import models
from django.utils.six import text_type, string_types
from django.utils.six.moves import range
from ... import random
from ...forms import RandomStringField as RandomStringFormField
from .base import RandomFieldMixin

default_valid_chars = text_type("23456789BCDFGHJKMNPQRSTVWXZ")
class RandomStringFieldMixin(RandomFieldMixin):
    def __init__(self, *args, **kwargs):
        try:
            max_length = int(kwargs["max_length"])
        except KeyError:
            raise TypeError("'max_length' is required")
        else:
            kwargs["max_length"] = max_length
            if not 0 < max_length:
                raise ValueError("'max_length' must be a positive integer.")
        
        try:
            min_length = int(kwargs.pop("min_length"))
        except KeyError:
            min_length = max_length
        else:
            if min_length < 0:
                raise ValueError("If set, 'min_length' must an integer greater than zero.")
            if max_length < min_length:
                raise ValueError("'min_length' cannot be larger than max_length.")
        self.min_length = min_length
        
        valid_chars = kwargs.pop("valid_chars", default_valid_chars)
        if not isinstance(valid_chars, string_types):
            raise TypeError("valid_chars must be of string type")
        self.valid_chars = text_type(valid_chars) 
        
        super(RandomStringFieldMixin, self).__init__(*args, **kwargs)
        
        if self.min_length == self.max_length:
            self.possibilities = len(self.valid_chars) ** self.max_length
        else:
            vcl = len(self.valid_chars)
            self.possibilities = sum([vcl ** n for n in range(self.min_length, self.max_length+1)])
    
    def random(self):
        length = random.randint(self.min_length, self.max_length)
        return text_type("").join([random.choice(self.valid_chars) for _ in range(length)])
        
    def formfield(self, **kwargs):
        defaults = {
            'max_length': self.max_length,
            'min_length': self.min_length,
            'valid_chars': self.valid_chars,
            'form_class': RandomStringFormField,
        }
        defaults.update(kwargs)
        return super(RandomStringFieldMixin, self).formfield(**defaults)

class RandomCharField(RandomStringFieldMixin, models.CharField):
    def check(self, **kwargs):
        errors = super(RandomCharField, self).check(**kwargs)
        if 255 < self.max_length:
            errors.append(checks.Warning(
                "It is recommended to restrict the CharField 'max_length' kwarg to 255 or less for database portability.",
                hint="Use 'RandomTextField' instead.",
                obj=self,
                id='%s.%s.MaxLengthGT255' % (__name__, self.__class__.__name__),
            ))
        return errors

class RandomTextField(RandomStringFieldMixin, models.TextField):
    def __init__(self, *args, **kwargs):
        super(RandomTextField, self).__init__(*args, **kwargs)
        self.validators.append(validators.MaxLengthValidator(self.max_length))