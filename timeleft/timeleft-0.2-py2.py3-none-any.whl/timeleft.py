#!/usr/bin/env python
# Written by  Sean Wareham on June 29th, 2015

"""
Program to tell you how much time is left on a download.  Simply call the program with two arguments making sure
to include the units for both file size and download speed.

Accounts for conversion between bits and bytes.

Examples:
    $ timeleft 100MB 100MBps
    1.0 second
    $ timeleft 100MB 100mbps
    8.0 seconds
    $ timeleft 100MB 100mb/s
    8.0 seconds
    $ timeleft 100MB 1kbps
    9.0 days, 11.0 hours, 33.0 minutes, 20.0 seconds
    $ 3.4GB 3.4MBps
    17.0 minutes, 4.0 seconds
    $ timeleft 1.5YB 10gbps
    28561641.0 years, 172.0 days, 10.0 hours, 21.0 minutes, 39.25 seconds
    $ timeleft 100GB 100GBPS
    1.0 second

"""

from __future__ import print_function
import sys
import re
import logging


SPEED = "speed"
SIZE = "size"


# Note: This uses binary base two as a base unit.
# This is easily configurable, but for the current use case this is
# irrelevant because the numerator and denominator will cancel out
BASE_UNIT = 1024

PREFIXES = {
    "b": 1,
    "B": 8,
    "K": BASE_UNIT,
    "M": BASE_UNIT ** 2,
    "G": BASE_UNIT ** 3,
    "T": BASE_UNIT ** 4,
    "P": BASE_UNIT ** 5,
    "E": BASE_UNIT ** 6,
    "Z": BASE_UNIT ** 7,
    "Y": BASE_UNIT ** 8,
}

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
rootLogger.setLevel(logging.ERROR)


class Measurement:
    """
    Class to handle parsing of speed and size units. Creation of an object automatically parses the input text.
    Raises RuntimeError on unknown unit type or improperly formatted input text.
    """
    def __init__(self, arg):
        rootLogger.log(logging.DEBUG, "Creating measurement for: \"" + arg + "\"")
        self.arg = arg
        # Match a numerical value (optionally a decimal) followed by an alpha string or the "/" character
        # Note: this does match "100." erroneously, but float("100.") = 100.0 so this is ok
        match = re.search('(\d+\.?\d*)([a-zA-Z/]+)', arg)
        # match = re.search('(\d+)([a-zA-Z/]+)', arg)
        if match is not None:
            # Regex matches only a number that exists so can cast as float safely
            self.number = float(match.group(1))
            self.unit = match.group(2)
            rootLogger.log(logging.DEBUG, "Number is: " + str(self.number) + " unit is: " + self.unit)
            self.base_amount = self._get_base_value(self.unit)
        else:
            raise RuntimeError("\"" + arg + "\" is not a valid number + unit of measure!")

    def __repr__(self):
        return "{Number: " + str(self.number) + ", Unit: " + self.unit + "}"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.get_type() == other.get_type() and \
               self.get_base_amount() == other.get_base_amount()

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_type(self):
        """
        Return the type of unit of measure (currently only speed and size)
        """
        if "/" in self.unit:
            return SPEED
        elif "ps" in self.unit.lower():
            return SPEED
        else:
            return SIZE

    def get_base_amount(self):
        """
        Return this measurement's value in base units
        e.g., 3 kilobits (using binary notation) = 3 * 1024 = 3072 bits

        For size, this is bits.
        For speed, this is bits per second
        """
        base_value = self._get_base_value(self.unit)
        base_amount = float(base_value) * self.number
        rootLogger.log(logging.DEBUG, "Base amount for measurement: \"" + self.arg + "\" is: " + str(base_amount))
        return base_amount

    @staticmethod
    def _get_prefix_multiplier(prefix):
        if prefix in PREFIXES:
            return PREFIXES[prefix]
        elif prefix.upper() in PREFIXES:
            return PREFIXES[prefix.upper()]
        else:
            raise RuntimeError("\"" + prefix + "\" is not a known unit prefix!")

    def _get_base_value(self, unit):
        # Match from a starting alpha character until the first instance of "/" "ps" or "PS
        # Also match case insensitive for ps
        match = re.search('^([a-zA-Z]+)(?:/|ps|PS|pS|Ps)', unit)
        if match is not None:
            relevant_unit = match.group(1)
        else:
            relevant_unit = unit
        base_amount = 1.0
        rootLogger.log(logging.DEBUG, "Relevant unit for \"" + unit + "\" is \"" + relevant_unit + "\"")
        for character in relevant_unit:
            base_amount *= self._get_prefix_multiplier(character)
        return base_amount


def get_measurements(args):
    """
    Return the measurements derived from the input args

    Input must be properly formatted i.e., an array of length two with one speed measurement and one size measurement.

    :param args: A properly formatted array of string arguments
    :return: A list of parsed measurements.
    """
    if len(args) != 2:
        raise RuntimeError("Must have exactly 2 arguments!")
    else:
        return [Measurement(arg) for arg in args]


def get_duration_seconds(measurements):
    """
    Return the number of seconds it takes to process a certain amount of data with a given rate of production.

    Generally used to calculate the amount of time to download a file (Bytes) using bandwidth (Bytes per second).

    Example:
    get_duration_seconds(['2GB', '1GB/s']) returns 2 (seconds)

    :param measurements: An iterable of parsed measurements.
    :return: The number of seconds to process a certain amount of data with a given rate of production
    """
    size = 0
    speed = 0
    for measurement in measurements:
        base_value = measurement.get_base_amount()
        if measurement.get_type() == SPEED:
            speed = base_value
        elif measurement.get_type() == SIZE:
            size = base_value
        else:
            raise RuntimeError("Must have a size unit and a speed unit!")
    if speed != 0 and size != 0:
        rootLogger.log(logging.DEBUG, "Size: " + str(size) + " Speed: " + str(speed))
        return float(size) / speed
    else:
        raise RuntimeError("Must have valid size and speed measurements!")


def get_human_time(seconds):
    """
    Return a string of human-readable time

    :param seconds: Seconds of time
    :return: String of human-readable time
    """

    if seconds < 1:
        return "{0:.2f}".format(seconds) + " seconds"

    years, remainder = divmod(seconds, 60*60*24*365)
    days, remainder = divmod(remainder, 60*60*24)
    hours, remainder = divmod(remainder, 60*60)
    minutes, seconds = divmod(remainder, 60)

    text = ""
    time_units = ["years", "days", "hours", "minutes", "second"]
    time_amounts = [years, days, hours, minutes, seconds]
    for i in range(0, len(time_units)):
        time_amount = time_amounts[i]
        if time_amount > 0:
            label = time_units[i]
            text += ", " + str(time_amount) + " " + label
            # Add s to seconds only when sensible
            if time_units[i] == "second" and time_amount != 1.0:
                text += "s"
    text = text.strip(", ")
    return text


def main():
    rootLogger.log(logging.INFO, "Starting main.")
    try:
        args = sys.argv[1:]
        measurements = get_measurements(args)
        seconds = get_duration_seconds(measurements)
        print(get_human_time(seconds))
        rootLogger.log(logging.INFO, "Execution Complete!")
    except RuntimeError as e:
        rootLogger.log(logging.ERROR, "RuntimeError: " + str(e))


if __name__ == "__main__":
    main()
