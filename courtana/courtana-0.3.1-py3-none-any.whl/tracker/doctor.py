# -*- coding: utf-8 -*-

"""
Doctor
======

The Doctor fixes the TrackData.
"""


class Doctor(object):

    """
    The Doctor looks at a TrackData object and reports its well being.
    For instance:
    - are the values in a column smooth, or are there big jumps?
    - how many values were lost, consecutive or not?

    It should also have the ability to fix some of the issues found.
    """

    def __init__(self):
        pass


if __name__ == '__main__':
    print(__file__)
    print(__doc__)
