from . import MultiValueError
from . import sanitize
from . import Test
from . import test_and_return
from . import validate
from pandora import check_mx_records
from pandora.compat import string_types
from pandora.compat import text_type
from poort.utils import FileStorage
from validate_email_address import validate_email
import bleach
import datetime as dt
import re

BOOL_FIELD_TRUE_VALUES = ['t', '1', 1, True, 'true', 'yes', 'True']
BOOL_FIELD_FALSE_VALUES = ['f', '-1', '0', -1, 0, False, 'false', 'no',
                           'False']
BOOL_FIELD_NONE_VALUES = ['null', 'none', None, 'None', 'undefined',
                          'Undefined']


def String(min_len=1, max_len=150,
           min_error='Too short.', max_error='Too long.',
           strip_html=True):
    commands = list()
    commands.append(lambda v: text_type(v))

    if min_len is not None:
        commands.append(validate(lambda v: len(v) >= min_len, min_error))
    if max_len is not None:
        commands.append(validate(lambda v: len(v) <= max_len, max_error))

    if strip_html:
        commands.append(lambda v: bleach.clean(v, tags=list(), strip=True))

    return Test(commands)


def Int(min_value=None, max_value=None, error='Not an integer.',
        min_error='Too low.', max_error='Too high.'):
    commands = list()
    commands.append(sanitize(int, error))

    if min_value is not None:
        commands.append(validate(lambda v: v >= min_value, min_error))
    if max_value is not None:
        commands.append(validate(lambda v: v <= max_value, max_error))

    return Test(commands)


def Float(min_value=None, max_value=None, error='Not a float.',
          min_error='Too low.', max_error='Too high.'):
    commands = list()
    commands.append(sanitize(float, error))

    if min_value is not None:
        commands.append(validate(lambda v: v >= min_value, min_error))
    if max_value is not None:
        commands.append(validate(lambda v: v <= max_value, max_error))

    return Test(commands)


def Boolean(false_values=None, true_values=None, true_unless_false=False,
            none_values=None, error='Not a boolean value.'):
    if false_values is None:
        false_values = BOOL_FIELD_FALSE_VALUES
    if true_values is None:
        true_values = BOOL_FIELD_TRUE_VALUES

    commands = list()

    if none_values is not None:
        commands.append(test_and_return(lambda v: v in none_values, None))

    if true_unless_false:
        commands.append(lambda v: v not in false_values)
    else:
        commands.append(test_and_return(lambda v: v in false_values, False))
        commands.append(test_and_return(lambda v: v in true_values, True))

    return Test(commands, mode=Test.OR, error_or=error)


def List(sanitize=None, split_character=','):
    test = Test([
        Test([
            validate(lambda v: isinstance(v, string_types)),
            validate(lambda v: len(v) > 0),
            lambda v: v.split(split_character),
        ]),
        Test([
            validate(lambda v: isinstance(v, (list, set,))),
        ]),
    ], mode=Test.OR)

    if sanitize:
        return Test([
            test,
            lambda v: [sanitize(x) for x in v],
        ])

    return test


def Enum(allowed_values, sanitize=None):
    if sanitize is None:
        sanitize = String()

    return Test([
        sanitize,
        validate(lambda v: v in allowed_values),
    ])


def Set(allowed_values, sanitize=None, split_character=','):
    return Test([
        List(sanitize, split_character),
        validate(lambda v: [x in allowed_values for x in v]),
    ])


def ListOf(test, sanitize=None, split_character=',',
           error='One or more errors found.'):
    def wrapper(value):
        errors = []
        result = []
        for row in value:
            try:
                result.append(test(row))
                errors.append(None)
            except ValueError as exc:
                errors.append(exc)

        if len([e for e in errors if e is not None]):
            raise MultiValueError(error, errors)
        else:
            return result

    return Test([
        List(sanitize, split_character),
        wrapper,
    ])


def InstanceOf(class_or_type_or_tuple, error='Not the required type.'):
    return Test([
        validate(lambda v: isinstance(v, class_or_type_or_tuple), error)
    ])


def Regex(pattern, error='Value invalid.'):
    pattern = re.compile(pattern)

    return Test([
        validate(lambda v: pattern.search(v) is not None, error)
    ])


_date_time_re = re.compile(
    '^'
    '[0-9]{4}-[0-9]{1,2}-[0-9]{1,2} '  # year-month-day
    '[0-9]{2}:[0-9]{2}(:[0-9]{2})?'  # hour:minute(:second)
    '$')

_date_re = re.compile(
    '^'
    '[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}'  # year-month-day
    '$')


def DateTime(pattern=None, formats=None,
             error='Invalid date-time format.',
             error_before_1900='Year before 1900.',
             error_after_today='Date in the future.'):
    if pattern is None:
        pattern = _date_time_re
    else:
        pattern = re.compile(pattern)

    if formats is None:
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
        ]

    def wrapper(value):
        for fmt in formats:
            try:
                return dt.datetime.strptime(value, fmt)
            except ValueError:
                continue

        raise ValueError(error, 'strptime')

    commands = [
        String(),
        Regex(pattern, error=error),
        wrapper,
    ]

    if error_before_1900:
        commands.append(validate(lambda v: v.year >= 1900, error_before_1900))

    if error_after_today:
        commands.append(validate(lambda v: v.date() <= dt.date.today(),
                                 error_after_today))

    return Test(commands)


def Date(pattern=None, formats=None,
         error='Invalid date format.',
         error_before_1900='Year before 1900.',
         error_after_today='Date in the future.'):
    if pattern is None:
        pattern = _date_re
    else:
        pattern = re.compile(pattern)

    if formats is None:
        formats = [
            '%Y-%m-%d',
        ]

    return Test([
        DateTime(pattern, formats, error,
                 error_before_1900, error_after_today),
        lambda v: v.date(),
    ])


def Email(error='Invalid e-mail address.',
          error_dot='Missing dot in e-mail address.',
          error_at='Missing at in e-mail address.',
          check_mx=False):
    commands = [
        String(min_len=5, max_len=256),
        validate(lambda v: '.' in v, error_dot),
        validate(lambda v: '@' in v, error_at),
        validate(lambda v: validate_email(v), error),
    ]

    if check_mx:
        commands.append(validate(lambda v: check_mx_records(v), error))

    return Test(commands)


def Upload(error='Invalid file upload.'):
    return Test([
        InstanceOf(FileStorage, error),
        validate(lambda v: v.secure_filename),
    ])
