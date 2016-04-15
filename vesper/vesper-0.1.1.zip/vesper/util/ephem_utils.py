"""
Utility functions related to sun and moon ephemerides.

This module includes functions that calculate:

- sunrise and sunset times
- civil, nautical, and astronomical dawn and dusk times
- moonrise and moonset times
- sun and moon altitudes and azimuths
- moon illumination.

The module relies on PyEphem (http://rhodesmill.org/pyephem) to calculate
these data.

[The following is no longer inaccurate and should be updated.]
See comments in the `test_ephem` script for the results of an extensive
comparison of times computed by PyEphem to times from tables computed
by the United States Naval Observatory (USNO). In short, thousands of
comparisons found no PyEphem times at latitudes below the polar circles
that differed from the corresponding USNO times by more than one minute,
with most in agreement. A small number of comparisons at latitudes above
the arctic circles found larger differences of up to five minutes. For
latitudes above the polar circles PyEphem also reports twilight dawn
and dusk times for some dates for which the USNO does not, and vice
versa.
"""


import collections
import datetime
import math

import ephem
import pytz


# We use the following since for some reason PyDev marks `ephem.Sun`
# (but not `ephem.Moon`!) as undefined.
_EPHEM_SUN = getattr(ephem, 'Sun')

_SUN = _EPHEM_SUN()
_MOON = ephem.Moon()

_BODY_FACTORIES = {
    'Sun': _EPHEM_SUN,
    'Moon': ephem.Moon
}

_RISE_SET_HORIZON = '-0:34'
_CIVIL_HORIZON = '-6'
_NAUTICAL_HORIZON = '-12'
_ASTRONOMICAL_HORIZON = '-18'

_EVENT_DATA = {
    'Sunrise': ('Rise', _SUN, _RISE_SET_HORIZON, False),
    'Sunset': ('Set', _SUN, _RISE_SET_HORIZON, False),
    'Civil Dawn': ('Rise', _SUN, _CIVIL_HORIZON, True),
    'Civil Dusk': ('Set', _SUN, _CIVIL_HORIZON, True),
    'Nautical Dawn': ('Rise', _SUN, _NAUTICAL_HORIZON, True),
    'Nautical Dusk': ('Set', _SUN, _NAUTICAL_HORIZON, True),
    'Astronomical Dawn': ('Rise', _SUN, _ASTRONOMICAL_HORIZON, True),
    'Astronomical Dusk': ('Set', _SUN, _ASTRONOMICAL_HORIZON, True),
    'Moonrise': ('Rise', _MOON, _RISE_SET_HORIZON, False),
    'Moonset': ('Set', _MOON, _RISE_SET_HORIZON, False)
}


# TODO: Put this in a separate module and parameterize capacity?
# TODO: Make caching optional?
def memoize(function):
    
    results_dict = {}
    results_deque = collections.deque()
    capacity = 100
    
    def aux(*args):
        
        key = tuple(args)
        
        try:
            return results_dict[key]
        
        except KeyError:
            
            result = function(*args)
            
            # Forget oldest result if at capacity.
            if len(results_deque) == capacity:
                key, _ = results_deque.popleft()
                del results_dict[key]

            # Cache new result.
            results_dict[key] = result
            results_deque.append((key, result))
            
            return result
    
    return aux


@memoize
def get_event_time(event, lat, lon, date):
    
    try:
        rise_set, body, horizon, use_center = _EVENT_DATA[event]
    except KeyError:
        raise ValueError('Unrecognized event "{}".'.format(event))

    function = _get_rising_time if rise_set == 'Rise' else _get_setting_time
    
    return function(lat, lon, date, body, horizon, use_center)

    
def _get_rising_time(lat, lon, date, body, horizon, use_center):
    method = ephem.Observer.next_rising
    return _get_time(method, lat, lon, date, body, horizon, use_center)


def _get_time(method, lat, lon, date, body, horizon, use_center):
    
    observer = _create_observer(lat, lon, horizon)

    midnight = _get_midnight_as_ephem_date(lon, date)
    
    try:
        ephem_date = method(
            observer, body, start=midnight, use_center=use_center)
    except ephem.CircumpolarError:
        return None
    else:
        return _get_datetime_from_ephem_date(ephem_date)
    
    
def _create_observer(lat, lon, horizon):
    observer = ephem.Observer()
    observer.lat = math.radians(lat)
    observer.lon = math.radians(lon)
    observer.horizon = horizon
    observer.pressure = 0
    return observer


def _get_midnight_as_ephem_date(lon, date):
    dt = datetime.datetime(date.year, date.month, date.day)
    dt -= datetime.timedelta(hours=lon * 24. / 360.)
    dt = pytz.utc.localize(dt)
    return dt.strftime('%Y/%m/%d %H:%M:%S')
    

def _get_datetime_from_ephem_date(ephem_date):
    year, month, day, hour, minute, float_second = ephem_date.tuple()
    second = int(math.floor(float_second))
    microsecond = int(round(1000000 * (float_second - second)))
    return datetime.datetime(
        year, month, day, hour, minute, second, microsecond, pytz.utc)


def _get_setting_time(lat, lon, date, body, horizon, use_center):
    method = ephem.Observer.next_setting
    return _get_time(method, lat, lon, date, body, horizon, use_center)


def get_altitude(body, lat, lon, time):
    body = _create_body(body, lat, lon, time)
    return math.degrees(float(body.alt))


def _create_body(body, lat, lon, time):
    
    try:
        factory = _BODY_FACTORIES[body]
    except KeyError:
        raise ValueError('Unrecognized body "{}".'.format(body))
    
    observer = ephem.Observer()
    observer.lat = math.radians(lat)
    observer.lon = math.radians(lon)
    observer.pressure = 0
    observer.date = time
    
    return factory(observer)


def get_azimuth(body, lat, lon, time):
    body = _create_body(body, lat, lon, time)
    return math.degrees(float(body.az))


def get_illumination(body, lat, lon, time):
    body = _create_body(body, lat, lon, time)
    return body.phase
