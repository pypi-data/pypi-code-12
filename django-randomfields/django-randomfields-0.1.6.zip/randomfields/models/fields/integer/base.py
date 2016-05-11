from django.core import checks
from django.db import models
from .... import random
from ..base import RandomFieldMixin

class RandomIntegerFieldMixin(RandomFieldMixin):
    lower_bound = None
    upper_bound = None
    
    def __init__(self, *args, **kwargs):
        super(RandomIntegerFieldMixin, self).__init__(*args, **kwargs)
        
        self.lower_bound = int(self.lower_bound)
        self.upper_bound = int(self.upper_bound)
        if self.upper_bound < self.lower_bound:
            raise ValueError("upper_bound may not be less than lower_bound")
        
        self.possibilities = self.upper_bound - self.lower_bound + 1
    
    def random(self):
        return random.randint(self.lower_bound, self.upper_bound)
    
    def formfield(self, **kwargs):
        defaults = {
            'min_value': self.lower_bound,
            'max_value': self.upper_bound,
        }
        defaults.update(kwargs)
        return super(RandomIntegerFieldMixin, self).formfield(**defaults)

class RandomBigIntegerField(RandomIntegerFieldMixin, models.BigIntegerField):
    # 8 byte / 64 bit Integer
    lower_bound = -9223372036854775808
    upper_bound = 9223372036854775807

class RandomIntegerField(RandomIntegerFieldMixin, models.IntegerField):
    # 4 byte / 32 bit Integer
    lower_bound = -2147483648
    upper_bound = 2147483647

class RandomSmallIntegerField(RandomIntegerFieldMixin, models.SmallIntegerField):
    # 2 byte / 16 bit Integer
    lower_bound = -32768
    upper_bound = 32767

class RandomNarrowIntegerField(RandomIntegerFieldMixin, models.IntegerField):
    """
        This field is a drop in replacement for AutoField primary keys.
        It returns a random integer between 1,000,000,000 and 2,147,483,647.
        These values were chosen specifically so that the string representation
        would be fixed length without requiring zero padding.
        
        This field uses a simpler approach to mimic the functionality of the
        identifier fields like `RandomBigIntegerIdentifierField`,
        `RandomIntegerIdentifierField`, and `RandomSmallIntegerIdentifierField`
        which cannot be reliably implemented under older versions of Django (< 1.8)
        due to lack of Field.from_db_value() support.
    """
    lower_bound = 1000000000
    upper_bound = 2147483647

class NarrowPositiveIntegerField(RandomNarrowIntegerField):
    def check(self, **kwargs):
        errors = super(NarrowPositiveIntegerField, self).check(**kwargs)
        errors.append(checks.Warning(
            'NarrowPositiveIntegerField has been deprecated.',
            hint='Use RandomNarrowIntegerField instead.',
            obj=self,
            id='%s.%s.Depreciated' % (__name__, self.__class__.__name__),
        ))
        return errors
