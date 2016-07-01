from __future__ import absolute_import, division, print_function

from pandora.compat import text_type
from pandora.compat import iteritems


class Undefined(object):
    pass


class Test(object):
    AND = '&'
    OR = '|'

    def __init__(self, commands, mode=AND, error_or='No test has passed.'):
        self.commands = commands
        self.mode = mode

        self.error_or = error_or

    def run(self, value):
        if self.mode == self.AND:
            return self.run_and(value)
        elif self.mode == self.OR:
            return self.run_or(value)
        else:
            raise RuntimeError('Invalid mode supplied.')

    def run_and(self, value):
        for command in self.commands:
            value = command(value)

        return value

    def run_or(self, value):
        for command in self.commands:
            try:
                return command(value)
            except ValueError:
                continue

        raise ValueError(self.error_or)

    def __call__(self, value):
        return self.run(value)


class MultiValueError(ValueError):
    def __init__(self, message, errors):
        super(MultiValueError, self).__init__(message)
        self.errors = errors

    @staticmethod
    def _recurse(value):
        if isinstance(value, MultiValueError):
            return value.to_dict()
        elif value is None:
            return value
        else:
            return str(value)

    def to_dict(self):
        return [self._recurse(v) for v in self.errors]


class MappedValueError(MultiValueError):
    def to_dict(self):
        return {k: self._recurse(v) for k, v in iteritems(self.errors)}


class Mapping(object):
    def __init__(self, schema):
        self.schema = list()

        for field_name in schema.keys():
            if not isinstance(field_name, Field):
                field = Field(field_name)
            else:
                field = field_name

            self.schema.append([field, schema[field_name]])

    def __call__(self, data, error='Validation error.',
                 error_required='Field is required.'):
        result = dict()
        errors = dict()

        for field, test in self.schema:
            field_name = str(field)

            if field_name not in data:
                if field.optional:
                    result[field_name] = field.default
                else:
                    errors[field_name] = error_required
            else:
                try:
                    result[field_name] = test(data[field_name])
                except ValueError as exc:
                    if field.soft and field.optional:
                        result[field_name] = field.default
                    elif field.soft:
                        result[field_name] = None
                    elif isinstance(exc, MultiValueError):
                        errors[field_name] = exc
                    else:
                        errors[field_name] = str(exc)

        if len(errors):
            raise MappedValueError(error, errors)

        return result


class Field(object):
    def __init__(self, name, default=Undefined, soft=False):
        self.name = name
        self.optional = default is not Undefined
        self.default = default
        self.soft = soft

    def __str__(self):
        return text_type(self.name)

    def __repr__(self):
        if self.optional:
            return '<Field {:s} [{:s}]>'.format(self.name, repr(self.default))
        else:
            return '<Field {:s}>'.format(self.name)


def validate(callback, error='Validation error.'):
    def wrapper(value):
        if not callback(value):
            raise ValueError(error)
        return value

    return wrapper


def sanitize(callback, error='Validation error.'):
    def wrapper(value):
        try:
            return callback(value)
        except:
            raise ValueError(error)

    return wrapper


def test_and_return(callback, return_value, error='Validation error.'):
    def wrapper(value):
        if callback(value):
            return return_value

        raise ValueError('Validation error.')

    return wrapper
