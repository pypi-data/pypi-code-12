'''
DateTimeEncoder: A custom encoder and decoder for serializing and de-serializing
datetime formats to ISO formats within JSON. Rather than use a 'type' indicator,
the de-serializer will check strings using regex to see if a string is actually
a date. While this adds an overhead, users of the package must decide if it is
worth the overhead or not.
'''
from datetime import datetime
import json
import re


class DateTimeEncoder(json.JSONEncoder):
    '''Custom encoder to enable the serialization of datetime objects as ISO
standard date formats. Use the object_hook with a call to decode to de-serialize
ISO dates.
    '''

    def default(self, o):
        if isinstance(o, datetime):
            try:
                return o.isoformat()
            except TypeError as te:
                raise TypeError('The date is badly formed.')
            except Exception as e:
                raise

        return json.JSONEncoder.default(self, o)


    @staticmethod
    def iso_date_match(date_string=None):
        """iso_date_match takes an input string and parses it for ISO date
format substrings (see https://en.wikipedia.org/wiki/ISO_8601). Any
strings found are replaced with Python dates. Valid input formats are:

    1. yyyy-mm-ddThh:mm:ss.msecZ : 2016-05-16T20:25:15.42113
    2. yyyy-mm-ddThh:mm:ssZ      : 2016-05-16T20:25:15
    3. yyyy-mm-dd hh:mm:ss.msecZ : 2016-05-16 20:25:15.42113
    4. yyyy-mm-dd hh:mm:ssZ      : 2016-05-16 20:25:15
    5. yyyy-mm-dd                : 2016-05-16
    6. yyyy-m-ddThh:mm:ss.msecZ : 2016-5-16T20:25:15.42113
    7. yyyy-m-ddThh:mm:ssZ      : 2016-5-16T20:25:15
    8. yyyy-m-dd hh:mm:ss.msecZ : 2016-5-16 20:25:15.42113
    9. yyyy-m-dd hh:mm:ssZ      : 2016-5-16 20:25:15
    10. yyyy-m-dd                : 2016-5-16

        """
        if date_string is None:
            return None
        if type(date_string) != str:
            raise TypeError('Date must be supplied as a string.')

        reg_ex_string = '\d{4}-\d{1,2}-\d{1,2}[T. ]\d{1,2}:\d{1,2}:\d{1,2}.\d{1,6}Z{0,1}'
        reg_ex_string += '|\d{4}-\d{1,2}-\d{1,2}[T. ]\d{1,2}:\d{1,2}:\d{1,2}Z{0,1}'
        reg_ex_string += '|\d{4}-\d{1,2}-\d{1,2}[T. ]\d{1,2}:\d{1,2}Z{0,1}'
        reg_ex_string += '|\d{4}-\d{1,2}-\d{1,2}'

        iso_reg_ex = re.compile(reg_ex_string)

        return iso_reg_ex.findall(date_string)

    @staticmethod
    def get_time_format(matched_string=None):
        """get_time_format compares a found ISO date string and sets the correct
    (or matching) python datetime format to be used in strptime.
        """
        if matched_string is None:
            raise ValueError(
                'The matched string cannot be {0} type'.format(type(None))
            )

        date_formats = {
            'yyyy-mm-ddXhh:mm:ss.s':
                ['\d{4}-\d{1,2}-\d{1,2}[T. ]\d{1,2}:\d{1,2}:\d{1,2}.\d{1,6}', '%Y-%m-%dT%H:%M:%S.%f'],
            'yyyy-mm-ddXhh:mm:ss':
                ['\d{4}-\d{1,2}-\d{1,2}[T. ]\d{1,2}:\d{1,2}:\d{1,2}', '%Y-%m-%dT%H:%M:%S'],
            'yyyy-mm-ddXhh:mm':
                ['\d{4}-\d{1,2}-\d{1,2}[T. ]\d{1,2}:\d{1,2}', '%Y-%m-%dT%H:%M'],
            'zyyyy-mm-ddXhh:mm:ss.s':
                ['\d{4}-\d{1,2}-\d{1,2}[T. ]\d{1,2}:\d{1,2}:\d{1,2}.\d{1,6}Z{1}', '%Y-%m-%dT%H:%M:%S.%fZ'],
            'zyyyy-mm-ddXhh:mm:ss':
                ['\d{4}-\d{1,2}-\d{1,2}[T. ]\d{1,2}:\d{1,2}:\d{1,2}Z{1}', '%Y-%m-%dT%H:%M:%SZ'],
            'zyyyy-mm-ddXhh:mm':
                ['\d{4}-\d{1,2}-\d{1,2}[T. ]\d{1,2}:\d{1,2}Z{1}', '%Y-%m-%dT%H:%MZ'],
            'yyyy-mm-dd':
                ['\d{4}-\d{1,2}-\d{1,2}', '%Y-%m-%d']
        }

        for d in sorted(date_formats, reverse=True):
            reg_ex = re.compile(date_formats[d][0])
            matches = reg_ex.findall(matched_string)
            if len(matches) > 0:
                return date_formats[d][1]

        raise TypeError('Invalid date format: {0}'.format(matched_string))

    @staticmethod
    def decode(obj):
        """Custom decoder to de-serialize ISO format dates in JSON back to Python
    datetime objects. This method is called for dict objects.
        """
        for key in obj.keys():
            if type(obj[key]) == list:
                obj[key] = list_time_decode(obj[key])

        match = DateTimeEncoder.iso_date_match(str(obj))

        if match != []:
            for m in match:
                # See ref below.
                try:
                    time_format = DateTimeEncoder.get_time_format(m)
                    # Needs to change to match values when the item is a list!
                    obj[list(obj.keys())[list(obj.values()).index(m)]] = \
                        datetime.strptime(m, time_format)
                except TypeError as te:
                    raise TypeError('The date is not in ISO format: {0}'.format(te))
                except ValueError as ve:
                    print()
                    print('*' * 78)
                    print('Value Error : {0}'.format(ve))
                    print('m is        : {0} '.format(m))
                    print('m is type   : {0}'.format(type(m)))
                    print('matches are : {0}'.format(match))
                    print(
                        'list values : {0}'.format(list(obj.values()))
                    )
                    print('list keys   : {0}'.format(list(obj.keys())))
                    print('*' * 78)
                    print()
                    pass
                except Exception:
                    raise

        return obj

    @staticmethod
    def string_time_decode(s):
        """Custom decoder to de-serialize ISO format dates in JSON back to Python
    datetime objects. This method is called when dates were serialized as a single
    item (rather than part of a document or object).
        """
        try:
            match = DateTimeEncoder.iso_date_match(s)
        except TypeError:
            raise

        if match != [] and len(match[0]) == len(s):
            time_format = DateTimeEncoder.get_time_format(match[0])
            s = datetime.strptime(match[0], time_format)
        else:
            raise TypeError('Unable to match date: is it UTC ISO format? yyyy-mm-dd hh:mm:ss.msec{Z}')
        return s

    @staticmethod
    def list_time_decode(l):
        """Custom decoder to de-serialize ISO format dates in JSON back to Python
    datetime objects. This method is called when dates were serialized as part of a
    list (rather than part of a document or object).
        """
        for idx, item in enumerate(l):
            if type(item) == str:
                match = DateTimeEncoder.iso_date_match(str(item))
                if match != [] and len(match[0]) == len(item):
                    time_format = DateTimeEncoder.get_time_format(match[0])
                    l[idx] = datetime.strptime(match[0], time_format)
            elif type(item) == list:
                l[idx] = DateTimeEncoder.list_time_decode(item)
        return l

#
# Reference: http://stackoverflow.com/questions/8023306/get-key-by-value-in-dictionary
#
# Amazing piece of Python to convert dict to list and lookup keys by values.
# Awesome!
