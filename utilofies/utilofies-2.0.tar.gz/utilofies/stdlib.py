# -*- encoding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import datetime
import json
import logging
import re
import signal
import socket
from copy import copy
from functools import wraps
from itertools import chain, islice
from logging import StreamHandler
from logging.handlers import SysLogHandler
from time import sleep


def subdict(source, mask):
    if isinstance(mask, dict):
        return {key: subdict(source[key], value)
                for key, value in mask.items()
                if key in source}
    else:
        return source


ZERO = datetime.timedelta(0)
HOUR = datetime.timedelta(hours=1)


# Code from pytz
class UTC(datetime.tzinfo):
    """UTC

    Optimized UTC implementation. It unpickles using the single module global
    instance defined beneath this class declaration.
    """
    zone = 'UTC'

    _utcoffset = ZERO
    _dst = ZERO
    _tzname = zone

    def fromutc(self, dt):
        if dt.tzinfo is None:
            return self.localize(dt)
        return super(utc.__class__, self).fromutc(dt)

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return 'UTC'

    def dst(self, dt):
        return ZERO

    def __reduce__(self):
        return _UTC, ()

    def localize(self, dt, is_dst=False):
        """Convert naive time to local time"""
        if dt.tzinfo is not None:
            raise ValueError('Not naive datetime (tzinfo is already set)')
        return dt.replace(tzinfo=self)

    def normalize(self, dt, is_dst=False):
        """Correct the timezone information on the given datetime"""
        if dt.tzinfo is self:
            return dt
        if dt.tzinfo is None:
            raise ValueError('Naive time - no tzinfo set')
        return dt.astimezone(self)

    def __repr__(self):
        return '<UTC>'

    def __str__(self):
        return 'UTC'


UTC = utc = UTC()  # UTC is a singleton


def myip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('8.8.8.8', 80))
    ip = sock.getsockname()[0]
    sock.close()
    return ip


def dictmerge(target, new, blacklist=()):
    if (type(target), type(new)) != (dict, dict):
        return new if new not in blacklist else target
    trivial = dict(target, **new)
    nested = dict((key, dictmerge(target[key], new[key], blacklist))
                  for key in set(target.keys()) & set(new.keys()))
    return dict(trivial, **nested)


def isoformat(date, default='0000-00-00T00:00:00.000000Z'):
    if not date:
        return
    try:
        date = date.astimezone(utc).replace(tzinfo=None)
    except ValueError:  # Naive datetime
        pass
    date = date.isoformat()
    return date + default[len(date):]


def canonicalized(item, blacklist=(None,)):
    """Converts JSON-compatible objects to their canonical representation,
    i.e., without keys with None values."""
    if type(item) == dict:
        return {key: value
                for key, value in ((key, canonicalized(value, blacklist))
                                   for key, value in item.iteritems())
                if value not in blacklist}
    elif type(item) == list:
        return [value for value
                in (canonicalized(value, blacklist) for value in item)
                if value not in blacklist]
    return item


def lgroupby(*args, **kwargs):
    return ((key, list(value)) for key, value in groupby(*args, **kwargs))


# https://github.com/mitsuhiko/werkzeug/blob/master/werkzeug/utils.py
class cached_property(object):
    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::

        class Foo(object):

            @cached_property
            def foo(self):
                # calculate something important here
                return 42

    The class has to have a `__dict__` in order for this property to
    work.
    """

    # implementation detail: this property is implemented as non-data
    # descriptor.  non-data descriptors are only invoked if there is
    # no entry with the same name in the instance's __dict__.
    # this allows us to completely get rid of the access function call
    # overhead.  If one choses to invoke __get__ by hand the property
    # will still work as expected because the lookup logic is replicated
    # in __get__ for manual invocation.

    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        if not obj.__dict__.has_key(self.__name__):
            obj.__dict__[self.__name__] = self.func(obj)
        return obj.__dict__[self.__name__]


# http://stackoverflow.com/questions/8464391
class Timeout(object):
    """Timeout class using ALARM signal"""

    class Timeout(Exception):
        pass

    def __init__(self, sec):
        self.sec = sec

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)

    def __exit__(self, *args):
        signal.alarm(0) # disable alarm

    def raise_timeout(self, *args):
        raise Timeout.Timeout('Timed out after {sec} s'.format(sec=self.sec))


def itertimeout(iterable, timeout):
    class TimeoutException(Exception):
        pass
    def raise_timeout(*args, **kwargs):
        raise TimeoutException(
            'Timeout ({timeout} s)'.format(timeout=timeout))
    signal.signal(signal.SIGALRM, raise_timeout)
    for item in iterable:
        signal.alarm(timeout)
        yield item
    signal.alarm(0)


def sub_slices(string, repls):
    parts = []
    last_stop = 0
    for (start, stop), repl in sorted(repls.items()):
        assert start >= last_stop, 'Intervals must not overlap'
        parts.append(string[last_stop:start])
        parts.append(repl)
        last_stop = stop
    parts.append(string[last_stop:])
    return ''.join(parts)


def itertrigger(iterable, triggers):
    for i, item in enumerate(iterable):
        for func, mod in triggers.items():
            if i % mod == 0:
                func()
        yield item


def sub_slices(string, repls):
    parts = []
    last_stop = 0
    for (start, stop), repl in sorted(repls.items()):
        assert start >= last_stop, 'Intervals must not overlap'
        parts.append(string[last_stop:start])
        parts.append(repl)
        last_stop = stop
    parts.append(string[last_stop:])
    return ''.join(parts)


def cached(cache):
    def decorator(func):
        @wraps(func)
        def wrapper(*args):
            try:
                return cache[args]
            except KeyError:
                value = func(*args)
                cache[args] = value
                return value
        return wrapper
    return decorator


# http://stackoverflow.com/questions/3203286
# http://stackoverflow.com/questions/5189699
class classproperty(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, owner):
        return self.func(owner)


def rechain(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        results = func(self, *args, **kwargs)
        return Chain(results)
    return wrapper


class Chain(object):

    def __init__(self, spout):
        self._spout = spout

    @property
    @rechain
    def chain(self):
        return chain.from_iterable(self._spout)

    @rechain
    def sleep(self, timeout):
        for entries in self._spout:
            sleep(timeout)
            yield entries

    @rechain
    def map(self, mapper, unpack=False):
        return (mapper(entry) if not unpack else mapper(**entry)
                for entry in self._spout)

    @rechain
    def behead(self, basket):
        for entries in self._spout:
            entries = iter(entries)
            for entry in entries:
                basket(entry)
                break
            yield entries

    def __iter__(self):
        return self._spout


class Underscore(object):

    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, attr):
        repl = lambda match: match.group(1).upper()
        ugly = re.sub('_([a-z0-9])', repl, attr)
        return getattr(self.obj, ugly)


class BaseJsonFormatter(logging.Formatter):
    """
    A custom formatter to format logging records as json strings.
    extra values will be formatted as str() if not supported by
    json default encoder.

    Sample rsyslog config:

        $ActionQueueType LinkedList    # Use asynchronous processing
        $ActionQueueFileName srvrfwd   # Set file name, also enables disk mode
        $ActionResumeRetryCount -1     # Infinite retries on insert failure
        $ActionQueueSaveOnShutdown on  # Save in-memory data if rsyslog shuts down
        $EscapeControlCharactersOnReceive off

        $template rawFormat, "%msg:2:$%\n"  # Cut off extraneous space
        $ActionFileDefaultTemplate rawFormat

        # Send everything to a logstash server on port 5544:
        local7.* @@luna.canterlot.gov:5544;rawFormat

    Sample Logstash config:

        input {
            tcp {
                port => 5544
                codec => line
            }
        }

        filter {
            json {
                source => "message"
            }
        }

        output {
            elasticsearch_http {
                host => "sparkle.canterlot.gov"
                index => "%{name}_%{+YYYY-MM}"
            }
        }
    """

    def __init__(self, *args, **kwargs):
        """
        :param json_default: a function for encoding non-standard objects
            as outlined in http://docs.python.org/2/library/json.html
        :param json_encoder: optional custom encoder
        """
        self.json_default = kwargs.pop('json_default', None)
        self.json_encoder = kwargs.pop('json_encoder', None)

        super(BaseJsonFormatter, self).__init__(*args, **kwargs)
        if not self.json_encoder and not self.json_default:
            def _default_json_handler(obj):
                """Prints dates in ISO format"""
                if isinstance(obj, datetime.datetime):
                    if self.datefmt:
                        return obj.strftime(self.datefmt)
                    return obj.isoformat()
                elif isinstance(obj, datetime.date):
                    return obj.strftime('%Y-%m-%d')
                elif isinstance(obj, datetime.time):
                    return obj.strftime('%H:%M')
                return str(obj)
            self.json_default = _default_json_handler

    def _context(self):
        return {'@timestamp': isoformat(datetime.datetime.utcnow())}

    def format(self, record):
        """Formats a log record and serializes to json"""
        log_record = self._context()
        log_record.update({
            key: value for key, value in vars(record).iteritems()
            if value not in (None, {}, [], (), '')})
        log_record['message'] = record.msg % record.args
        # remove exception info if None
        if 'exc_info' in log_record and not log_record['exc_info']:
            del log_record['exc_info']
        if 'exc_text' in log_record and not log_record['exc_text']:
            del log_record['exc_text']
        # The “…: ” has to be there for some reason, otherwise rsyslog
        # crops of part of the JSON till the first colon plus space.
        line = '{}: {}'.format(log_record['name'], json.dumps(
            log_record, default=self.json_default, cls=self.json_encoder))
        return line


class ExtraFormatter(logging.Formatter):

    BUILTIN_KEYS = set(('args', 'created', 'exc_info', 'exc_text', 'filename',
                        'funcName', 'getMessage', 'levelname', 'levelno',
                        'lineno', 'module', 'msecs', 'msg', 'name', 'pathname',
                        'process', 'processName', 'relativeCreated', 'thread',
                        'threadName'))

    def format(self, record):
        extra = {key: value for key, value in vars(record).items()
                 if not key.startswith('_') and key not in self.BUILTIN_KEYS}
        line = super(ExtraFormatter, self).format(record)
        suffix = json.dumps(extra, sort_keys=True, default=repr)
        return '{} {}'.format(line, suffix)


def get_logstash_logger(name, level=logging.INFO):
    stream_handler = StreamHandler()
    stream_handler.setFormatter(BaseJsonFormatter())
    syslog_handler = SysLogHandler(
        address=('localhost', 514), facility=SysLogHandler.LOG_LOCAL7)
    syslog_handler.setFormatter(BaseJsonFormatter())
    logger = logging.getLogger(name)
    logger.addHandler(stream_handler)
    logger.addHandler(syslog_handler)
    logger.setLevel(level)
    return logger


# An approximation of abbreviation translations: “I looked at each
# conflict and resolved conflicts between obscure and popular names
# towards the popular (more used ones).”
# http://stackoverflow.com/a/4766400/678861
TZINFOS = {
    'A': 1 * 60 * 60,
    'ACDT': 10 * 60 * 60,
    'ACST': 9 * 60 * 60,
    'ACT': 8 * 60 * 60,
    'ADT': -3 * 60 * 60,
    'AEDT': 11 * 60 * 60,
    'AEST': 10 * 60 * 60,
    'AFT': 4 * 60 * 60,
    'AKDT': -8 * 60 * 60,
    'AKST': -9 * 60 * 60,
    'ALMT': 6 * 60 * 60,
    'AMST': 5 * 60 * 60,
    'AMT': 4 * 60 * 60,
    'ANAST': 12 * 60 * 60,
    'ANAT': 12 * 60 * 60,
    'AQTT': 5 * 60 * 60,
    'ART': -3 * 60 * 60,
    'AST': -4 * 60 * 60,
    'AWDT': 9 * 60 * 60,
    'AWST': 8 * 60 * 60,
    'AZOT': -1 * 60 * 60,
    'AZST': 5 * 60 * 60,
    'AZT': 4 * 60 * 60,
    'B': 2 * 60 * 60,
    'BDT': 8 * 60 * 60,
    'BIOT': 6 * 60 * 60,
    'BNT': 8 * 60 * 60,
    'BOT': -4 * 60 * 60,
    'BRST': -2 * 60 * 60,
    'BRT': -3 * 60 * 60,
    'BTT': 6 * 60 * 60,
    'C': 3 * 60 * 60,
    'CAST': 8 * 60 * 60,
    'CAT': 2 * 60 * 60,
    'CCT': 6 * 60 * 60,
    'CDT': -5 * 60 * 60,
    'CEDT': 2 * 60 * 60,
    'CEST': 2 * 60 * 60,
    'CET': 1 * 60 * 60,
    'CIST': -8 * 60 * 60,
    'CKT': -10 * 60 * 60,
    'CLST': -3 * 60 * 60,
    'CLT': -4 * 60 * 60,
    'COST': -4 * 60 * 60,
    'COT': -5 * 60 * 60,
    'CST': -6 * 60 * 60,
    'CVT': -1 * 60 * 60,
    'CXT': 7 * 60 * 60,
    'ChST': 10 * 60 * 60,
    'D': 4 * 60 * 60,
    'DAVT': 7 * 60 * 60,
    'DFT': 1 * 60 * 60,
    'E': 5 * 60 * 60,
    'EASST': -5 * 60 * 60,
    'EAST': -6 * 60 * 60,
    'EAT': 3 * 60 * 60,
    'ECT': -5 * 60 * 60,
    'EDT': -4 * 60 * 60,
    'EEDT': 3 * 60 * 60,
    'EEST': 3 * 60 * 60,
    'EET': 2 * 60 * 60,
    'EGST': 0 * 60 * 60,
    'EGT': -1 * 60 * 60,
    'EST': -5 * 60 * 60,
    'ET': -5 * 60 * 60,
    'F': 6 * 60 * 60,
    'FJST': 13 * 60 * 60,
    'FJT': 12 * 60 * 60,
    'FKST': -3 * 60 * 60,
    'FKT': -4 * 60 * 60,
    'FNT': -2 * 60 * 60,
    'G': 7 * 60 * 60,
    'GALT': -6 * 60 * 60,
    'GAMT': -9 * 60 * 60,
    'GET': 4 * 60 * 60,
    'GFT': -3 * 60 * 60,
    'GILT': 12 * 60 * 60,
    'GIT': -9 * 60 * 60,
    'GMT': 0 * 60 * 60,
    'GST': 4 * 60 * 60,
    'GYT': -4 * 60 * 60,
    'H': 8 * 60 * 60,
    'HAA': -3 * 60 * 60,
    'HAC': -5 * 60 * 60,
    'HADT': -9 * 60 * 60,
    'HAE': -4 * 60 * 60,
    'HAP': -7 * 60 * 60,
    'HAR': -6 * 60 * 60,
    'HAST': -10 * 60 * 60,
    'HAT': -2 * 60 * 60,
    'HAY': -8 * 60 * 60,
    'HKT': 8 * 60 * 60,
    'HLV': -4 * 60 * 60,
    'HMT': 5 * 60 * 60,
    'HNA': -4 * 60 * 60,
    'HNC': -6 * 60 * 60,
    'HNE': -5 * 60 * 60,
    'HNP': -8 * 60 * 60,
    'HNR': -7 * 60 * 60,
    'HNT': -3 * 60 * 60,
    'HNY': -9 * 60 * 60,
    'HOVT': 7 * 60 * 60,
    'HST': -10 * 60 * 60,
    'I': 9 * 60 * 60,
    'ICT': 7 * 60 * 60,
    'IDT': 3 * 60 * 60,
    'IOT': 6 * 60 * 60,
    'IRDT': 4 * 60 * 60,
    'IRKST': 9 * 60 * 60,
    'IRKT': 8 * 60 * 60,
    'IRST': 3 * 60 * 60,
    'JST': 9 * 60 * 60,
    'K': 10 * 60 * 60,
    'KGT': 6 * 60 * 60,
    'KRAST': 8 * 60 * 60,
    'KRAT': 7 * 60 * 60,
    'KST': 9 * 60 * 60,
    'KUYT': 4 * 60 * 60,
    'L': 11 * 60 * 60,
    'LHDT': 11 * 60 * 60,
    'LHST': 10 * 60 * 60,
    'M': 12 * 60 * 60,
    'MAGST': 12 * 60 * 60,
    'MAGT': 11 * 60 * 60,
    'MART': -9 * 60 * 60,
    'MAWT': 5 * 60 * 60,
    'MDT': -6 * 60 * 60,
    'MHT': 12 * 60 * 60,
    'MIT': -9 * 60 * 60,
    'MMT': 6 * 60 * 60,
    'MSD': 4 * 60 * 60,
    'MSK': 3 * 60 * 60,
    'MST': -7 * 60 * 60,
    'MUT': 4 * 60 * 60,
    'MVT': 5 * 60 * 60,
    'MYT': 8 * 60 * 60,
    'N': -1 * 60 * 60,
    'NCT': 11 * 60 * 60,
    'NDT': -2 * 60 * 60,
    'NFT': 11 * 60 * 60,
    'NOVST': 7 * 60 * 60,
    'NOVT': 6 * 60 * 60,
    'NPT': 5 * 60 * 60,
    'NST': -3 * 60 * 60,
    'NT': -3 * 60 * 60,
    'NUT': -11 * 60 * 60,
    'NZDT': 13 * 60 * 60,
    'NZST': 12 * 60 * 60,
    'O': -2 * 60 * 60,
    'OMSST': 7 * 60 * 60,
    'OMST': 6 * 60 * 60,
    'P': -3 * 60 * 60,
    'PDT': -7 * 60 * 60,
    'PET': -5 * 60 * 60,
    'PETST': 12 * 60 * 60,
    'PETT': 12 * 60 * 60,
    'PGT': 10 * 60 * 60,
    'PHT': 8 * 60 * 60,
    'PKT': 5 * 60 * 60,
    'PMDT': -2 * 60 * 60,
    'PMST': -3 * 60 * 60,
    'PONT': 11 * 60 * 60,
    'PST': -8 * 60 * 60,
    'PT': -8 * 60 * 60,
    'PWT': 9 * 60 * 60,
    'PYST': -3 * 60 * 60,
    'PYT': -4 * 60 * 60,
    'Q': -4 * 60 * 60,
    'R': -5 * 60 * 60,
    'RET': 4 * 60 * 60,
    'S': -6 * 60 * 60,
    'SAMT': 4 * 60 * 60,
    'SAST': 2 * 60 * 60,
    'SBT': 11 * 60 * 60,
    'SCT': 4 * 60 * 60,
    'SGT': 8 * 60 * 60,
    'SLT': 5 * 60 * 60,
    'SRT': -3 * 60 * 60,
    'SST': -11 * 60 * 60,
    'T': -7 * 60 * 60,
    'TAHT': -10 * 60 * 60,
    'TFT': 5 * 60 * 60,
    'THA': 7 * 60 * 60,
    'TJT': 5 * 60 * 60,
    'TKT': -10 * 60 * 60,
    'TLT': 9 * 60 * 60,
    'TMT': 5 * 60 * 60,
    'TVT': 12 * 60 * 60,
    'U': -8 * 60 * 60,
    'ULAT': 8 * 60 * 60,
    'UTC': 0 * 60 * 60,
    'UYST': -2 * 60 * 60,
    'UYT': -3 * 60 * 60,
    'UZT': 5 * 60 * 60,
    'V': -9 * 60 * 60,
    'VET': -4 * 60 * 60,
    'VLAST': 11 * 60 * 60,
    'VLAT': 10 * 60 * 60,
    'VUT': 11 * 60 * 60,
    'W': -10 * 60 * 60,
    'WAST': 2 * 60 * 60,
    'WAT': 1 * 60 * 60,
    'WDT': 9 * 60 * 60,
    'WEDT': 1 * 60 * 60,
    'WEST': 1 * 60 * 60,
    'WET': 0 * 60 * 60,
    'WFT': 12 * 60 * 60,
    'WGST': -2 * 60 * 60,
    'WGT': -3 * 60 * 60,
    'WIB': 7 * 60 * 60,
    'WIT': 9 * 60 * 60,
    'WITA': 8 * 60 * 60,
    'WST': 8 * 60 * 60,
    'WT': 0 * 60 * 60,
    'X': -11 * 60 * 60,
    'Y': -12 * 60 * 60,
    'YAKST': 10 * 60 * 60,
    'YAKT': 9 * 60 * 60,
    'YAPT': 10 * 60 * 60,
    'YEKST': 6 * 60 * 60,
    'YEKT': 5 * 60 * 60,
    'Z': 0 * 60 * 60,
}


TZINFOS.update({
    'WEZ': 0 * 60 * 60,
    'WESZ': 1 * 60 * 60,
    'MEZ': 1 * 60 * 60,
    'MESZ': 2 * 60 * 60,
    'OEZ': 2 * 60 * 60,
    'OESZ': 3 * 60 * 60,
})
