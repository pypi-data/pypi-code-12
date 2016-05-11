from django.core import checks
from django.utils.encoding import force_text
from django.utils.six import text_type, integer_types, string_types
from itertools import chain
from functools import total_ordering
from ....checks import DJANGO_VERSION_LT_18
from .base import RandomBigIntegerField, RandomIntegerField, RandomSmallIntegerField

@total_ordering
class IntegerIdentifier(text_type):
    db_value = None
    display_value = None
    display_str = None
    lower_bound = None
    upper_bound = None
    possibilities = None
    
    def __new__(cls, value, possibilities, lower_bound, upper_bound):
        # verify types are acceptable
        value = int(value)
        possibilities = int(possibilities)
        lower_bound = int(lower_bound)
        upper_bound = int(upper_bound)
        
        # verify values are acceptable
        if not 0 < possibilities:
            # this is the only check performed for possibilities at the moment.
            # we do not know the acceptable values between lower_bound and
            # upper_bound so we cannot validate the possibility count
            raise ValueError("possibilities must be a positive integer")
        
        if not lower_bound < upper_bound:
            raise ValueError("upper_bound must be greater than lower_bound")
        
        # for 32 bit int, possibilities is 4,294,967,296
        # because the possible unsigned values are [0, 4294967295]
        # In this case, map 0 to 4,294,967,296 and map
        # 4,294,967,295 to 8,589,934,591
        discriminator = possibilities - abs(lower_bound)
        if value < discriminator:
            display_value = value + possibilities
            db_value = value
        else:
            display_value = value
            db_value = value - possibilities
        
        length = len(text_type(possibilities + upper_bound))
        
        display_str = text_type(display_value).zfill(length)
        
        self = super(IntegerIdentifier, cls).__new__(cls, display_str)
        self.db_value = db_value
        self.display_value = display_value
        self.display_str = display_str
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.possibilities = possibilities
        
        return self
    
    def __int__(self):
        return self.db_value

    def _values_for_comparison(self, other):
        value = None
        known_types = tuple(chain(string_types, integer_types, [IntegerIdentifier]))
        if not isinstance(other, known_types):
            try:
                other = int(other)
            except (TypeError, ValueError):
                try:
                    other = force_text(other)
                except (TypeError, ValueError):
                    pass
        if isinstance(other, integer_types):
            other = IntegerIdentifier(other, self.possibilities, self.lower_bound, self.upper_bound)
        if isinstance(other, IntegerIdentifier):
            value = int(self)
            other = int(other)
        if isinstance(other, string_types):
            value = text_type(self)
            if not isinstance(other, text_type):
                other = force_text(other)
        if value is None:
            raise TypeError("Could not compare against other type '%s'" % type(other))
        return value, other
        
    def __eq__(self, other):
        value, other = self._values_for_comparison(other)
        return value == other
    
    def __lt__(self, other):
        value, other = self._values_for_comparison(other)
        return value < other
    
    def __hash__(self):
        return hash(text_type("{};{}").format(int(self), self))

class RandomIntegerIdentifierFieldMixin(object):
    def to_python(self, value):
        if value is not None and not isinstance(value, IntegerIdentifier):
            value = IntegerIdentifier(value, self.possibilities, self.lower_bound, self.upper_bound)
        return value
    
    def get_prep_value(self, value):
        if value is not None:
            value = self.to_python(value).db_value
        return value
    
    def get_db_prep_value(self, *args, **kwargs):
        value = super(RandomIntegerIdentifierFieldMixin, self).get_db_prep_value(*args, **kwargs)
        if isinstance(value, IntegerIdentifier):
            value = int(value)
        return value
    
    def from_db_value(self, value, *args):
        return self.to_python(value)
    
    def random(self):
        value = super(RandomIntegerIdentifierFieldMixin, self).random()
        return IntegerIdentifier(value, self.possibilities, self.lower_bound, self.upper_bound)
    
    def formfield(self, **kwargs):
        defaults = {
            'min_value': IntegerIdentifier(self.lower_bound, self.possibilities, self.lower_bound, self.upper_bound).display_value,
            'max_value': IntegerIdentifier(self.upper_bound, self.possibilities, self.lower_bound, self.upper_bound).display_value,
        }
        defaults.update(kwargs)
        return super(RandomIntegerIdentifierFieldMixin, self).formfield(**defaults)
    
    def check(self, **kwargs):
        errors = super(RandomIntegerIdentifierFieldMixin, self).check(**kwargs)
        if DJANGO_VERSION_LT_18:
            errors.append(checks.Critical(
                'IntegerIdentifier fields are not supported on Django versions less than 1.8.',
                hint='Use RandomNarrowIntegerField instead.',
                obj=self,
                id='%s.RandomIntegerIdentifierFieldMixin.Unsupported' % __name__,
            ))
        return errors

class RandomBigIntegerIdentifierField(RandomIntegerIdentifierFieldMixin, RandomBigIntegerField):
    pass

class RandomIntegerIdentifierField(RandomIntegerIdentifierFieldMixin, RandomIntegerField):
    pass

class RandomSmallIntegerIdentifierField(RandomIntegerIdentifierFieldMixin, RandomSmallIntegerField):
    pass