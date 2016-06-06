'''dhp transforms library'''
from __future__ import division
from __future__ import print_function
import re

RE_FIRST_CAP = re.compile('(.)([A-Z][a-z]+)')
RE_ALL_CAP = re.compile('([a-z0-9])([A-Z])')


def to_snake(buf):
    """pythonize the camelCased name contained in buf

    >>> to_snake('camelCase')
    camel_case

    Args:
        buf (str): the camelCased name to transform

    Returns:
        str: the pythonized version of the camelCased name
    """
    # attribution: http://stackoverflow.com/questions/1175208
    intermediate = RE_FIRST_CAP.sub(r'\1_\2', buf)
    intermediate = RE_ALL_CAP.sub(r'\1_\2', intermediate).lower()
    return intermediate.replace('__', '_')


def chunk_r(buf, chunk_size):
    """starting from the right most character, split into groups of chunk_size.

    >>> chunk_r('abcdefg', 3)
    ['a', 'bcd', 'efg']

    Args:
        buf (str): a string or object that can be stringified
        chunk_size (int): the maximum size of the groups

    Returns:
        list: chunk_sized strings

    """
    val = str(buf)[:]
    rslt = []
    while val:
        rslt.insert(0, val[-chunk_size:])
        val = val[:-chunk_size]
    return rslt


def int2word(ivalue):
    """return the integer value as word(s)

    >>> int2word(12)
    Twelve
    >>> int2word(237)
    Two Hundred Thirty Seven

    Args:
        ivalue (int): the integer to be converted

    Returns:
        str: The spelled out value of ivalue

    """
    spec = {
        0: "Zero",
        1: "One",
        2: "Two",
        3: "Three",
        4: "Four",
        5: "Five",
        6: "Six",
        7: "Seven",
        8: "Eight",
        9: "Nine",
        10: "Ten",
        11: "Eleven",
        12: "Twelve",
        13: "Thirteen",
        14: "Fourteen",
        15: "Fifteen",
        16: "Sixteen",
        17: "Seventeen",
        18: "Eighteen",
        19: "Nineteen",
        20: "Twenty",
        30: "Thirty", 40: "Forty", 50: "Fifty", 60: "Sixty",
        70: "Seventy", 80: "Eighty", 90: "Ninety"
    }
    pow_tens = ["Quadrillion", "Trillion", "Billion", "Million", "Thousand",
                ""]
    parts = chunk_r(ivalue, 3)
    pow_tens = pow_tens[-len(parts):]
    buf = ''
    for part in parts:
        pow_flag = False
        if len(part) == 3:
            hundreds = int(part[0])
            if hundreds:
                pow_flag = True
                buf += " " + spec[hundreds] + " Hundred"
        try:
            remainder = int(part[-2:])
            if part[-2:] != '00':
                pow_flag = True
                buf += " " + spec[remainder]
        except KeyError:
            tens, ones = divmod(remainder, 10)
            buf += " " + int2word(tens * 10) + " " + int2word(ones)
        powten = pow_tens.pop(0)
        if pow_flag:
            buf += " " + powten
    return buf.strip()


def filter_dict(dictionary, keys):
    """filter a dicitionary so it contains only specified keys.

    >>> old = {'foo': 0, 'bar': 1, 'baz': 2}
    >>> filter_dict(old, ['bar', 'baz', 'missing'])
    {'bar': 1, 'baz': 2}

    Args:
        dictionary (dict): the dictionary to filter out unwanted keys/vals
        keys (list): the list of keys to return in the resultant dicitionary

    Returns:
        dict: the resultant dictionary with only the specified keys

    """

    return {key: dictionary[key] for key in set(keys) & set(dictionary.keys())}
