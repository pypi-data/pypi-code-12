"""
Ingress Cycle/Checkpoint class
"""

from datetime import datetime, timedelta
from timestring import Date

import pytz
from tzlocal import get_localzone

CYCLE_HOURS = 7*25
CHECKPOINT_HOURS = 5
CHECKPOINTS_IN_CYCLE = 35


class DeltaTime(object):
    """Generic delta time base class"""
    def __init__(self, delta, target=None, timezone=None):
        if not timezone:
            self.timezone = get_localzone()
        elif isinstance(timezone, str):
            self.timezone = self._tz_normalize(timezone)
        else:
            self.timezone = timezone

        if not target:
            target = datetime.now(self.timezone)
        elif isinstance(target, int) or isinstance(target, float):
            target = datetime.fromtimestamp(target).replace(tzinfo=pytz.utc)
        elif isinstance(target, str):
            target = Date(target).date.replace(tzinfo=self.timezone)

        target = target.replace(microsecond=0)
        target_ts = target.timestamp()
        delta_secs = delta.total_seconds()

        self.delta = delta
        self.start = datetime.fromtimestamp((target_ts // delta_secs) * delta_secs, self.timezone)
        self.end = self.start + self.delta
        self.target = target

    @staticmethod
    def _tz_normalize(timezone):
        name = timezone.lower().strip()
        for zone in pytz.all_timezones:
            if name == zone.lower():
                return pytz.timezone(zone)
        raise pytz.exceptions.UnknownTimeZoneError(timezone)

    def since_last(self, target=None):
        """Return timedelta object for time since start of cycle"""
        return (target or self.target) - self.start

    def until_next(self, target=None):
        """Return timedelta object for time since end of cycle"""
        return self.start + self.delta - (target or self.target)

    @staticmethod
    def friendly_delta(delta):
        """Normalize timedelta to human friendly"""
        if delta < timedelta(0):
            return 'in ' + str(-delta)
        else:
            return '' + str(delta) + ' ago'

    def __repr__(self):
        # pylint: disable=locally-disabled,no-member
        return "{}.{}({}, {}, {})".format(
            self.__class__.__module__, self.__class__.__qualname__,
            repr(self.delta), repr(self.target), repr(self.timezone))

    def __str__(self):
        return "{:%a, %b %d %Y %I:%M %p %Z}".format(self.start)

    def __int__(self):
        return int(self.start.timestamp())

    def __float__(self):
        return self.start.timestamp()

    def __iter__(self):
        return self

    def __next__(self):
        self.target += self.delta
        self.start += self.delta
        self.end = self.start + self.delta
        return self

    def __add__(self, other):
        if not isinstance(other, int):
            raise NotImplementedError("can only add integers")
        newtarget = self.target + (self.delta * other)
        # pylint: disable=locally-disabled,undefined-variable
        return __class__(self.delta, target=newtarget, timezone=self.timezone)

    def __sub__(self, other):
        if not isinstance(other, int):
            raise NotImplementedError("can only subtract integers")
        newtarget = self.target - (self.delta * other)
        # pylint: disable=locally-disabled,undefined-variable
        return __class__(self.delta, target=newtarget, timezone=self.timezone)

    def __iadd__(self, other):
        self.target += (self.delta * other)
        self.start += (self.delta * other)
        self.end = self.start + self.delta
        return self

    def __isub__(self, other):
        self.target -= (self.delta * other)
        self.start -= (self.delta * other)
        self.end = self.start + self.delta
        return self

    def __eq__(self, other):
        return self.start == other.start and self.delta == other.delta

    def __lt__(self, other):
        return self.start < other.start and self.delta == other.delta


class Cycle(DeltaTime):
    """Ingress Scoring Cycle (7 25 hour days)"""
    def __init__(self, target=None, timezone=None):
        super().__init__(timedelta(hours=CYCLE_HOURS), target, timezone)


class Checkpoint(DeltaTime):
    """Ingress Checkpoint Cycle (every 5 hours)"""
    def __init__(self, target=None, timezone=None):
        super().__init__(timedelta(hours=CHECKPOINT_HOURS), target, timezone)

    def number(self):
        """Return the number of checkpoints into its cycle this checkpoint is

        The start of the cycle is also the last checkpoint in the previous cycle.
        """
        num = int((self.start - Cycle(self.start, timezone=self.timezone).start) / self.delta)
        return CHECKPOINTS_IN_CYCLE if num == 0 else num

    def cycle_start(self):
        """Return true if this checkpoint is the start of a cycle"""
        return self.start == Cycle(self.start, timezone=self.timezone).start

    def on_day(self):
        """Return an iterable of checkpoints for the day already provided"""
        day_start = self.target.replace(hour=0, minute=0, second=0)
        day_end = day_start + timedelta(hours=24)
        for point in Checkpoint(day_start, timezone=self.timezone):
            if point.start > day_end:
                break
            yield point
