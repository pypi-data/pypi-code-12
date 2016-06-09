# -*- coding: utf-8 -*-
import re

def parseoncolon(s):
    """Parse a string of arguments separated by colon.

    (?=[ ^\s:]+:) Positive Lookahead - Assert that the regex below
    can be matched
    [ ^\s:]+ match a single character not present in the list below
    Quantifier: + Between one and unlimited times, as many times as possible, giving
    back as needed[greedy]
    \s match any white space character[\r\n\t\f]
    : the literal character:
    : matches the character: literally

    :param s:
    """

    al = re.split(r' (?=[^\s:]+:)', s)
    #al = [i.encode('ascii') for i in al]
    d = {}

    for i in al:
        k, v = i.split(':')
        d[k] = v

    # return the dictionary
    return d