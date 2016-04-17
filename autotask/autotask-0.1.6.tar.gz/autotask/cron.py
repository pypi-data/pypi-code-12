
import calendar
import datetime
import re

from django.conf import settings
from django.utils.timezone import (
    localtime,
    make_aware,
    now,
)


class CronScheduler:
    """
    Schedules a cron task.

    Usage:

    cs = CronScheduler()
    next_schedule = cs.get_next_schedule()
    """

    def __init__(self, last_schedule=None, minutes=None, hours=None,
                 dow=None, months=None, dom=None, crontab=None):
        """
        Inits the scheduler with values according the crontab-format.

        All arguments are optional. If no arguments are given the task
        is scheduled from now on every minute.

        last_schedule: last time the according tasks has run
        minutes: list of integers when a task should run in an hour [0-59]
        hours: list of integers when a task should run during a day [0-23]
        dow: list of integers for the days of week when a task should
        run [0-6] (0 for monday up to 6 for sunday).
        month: list of integers for the months a task should run [1-12]
        dom: list of intergs for the day in a month a task should run [1-31]
        """
        self.date = last_schedule or now()
        if not self.parse_crontab(crontab):
            self.minutes = minutes
            self.hours = hours
            self.dow = dow
            self.months = months
            self.dom = dom

    def parse_crontab(self, crontab):
        """
        Parses a simple crontab-string with five patterns:

        Minute [0,59]
        Hour [0,23]
        Day of the month [1,31]
        Month of the year [1,12]
        Day of the week ([0,6] with 0=Sunday)

        Each of these patterns can be either an asterisk (meaning all
        valid values), an element, or a list of elements separated by
        commas. An element shall be either a number or two numbers
        separated by a hyphen (meaning an inclusive range).

        A day-range for a month like 1-4,12,20-25 is also ok. But keep
        in mind that no spaces are allowed as spaces are the separators
        between the patterns.

        Some examples:

        * * * * *               runs every minute
        5 * * * *               runs every five minutes
        30 7 10-15 4,7 0        runs at 7:30 on mondays and also from the
                                10th to 15th of a month, but only in april
                                and july

        Returns a boolean whether the crontab could be parsed (with the
        content *not* checked for correctness).
        """
        if not crontab:
            return False
        outer = []
        for item in crontab.split():
            item = item.strip()
            if item == '*':
                outer.append(None)
                continue
            inner = []
            for element in item.split(','):
                mo = re.match(r'(\d+)-(\d+)', element)
                if mo:
                    inner.extend([i for i in range(
                        int(mo.group(1)), int(mo.group(2))+1)])
                else:
                    inner.append(int(element))
            outer.append(inner)
        if len(outer) == 5:
            self.minutes, self.hours, self.dom, self.months, self.dow = outer
            return True
        return False

    def get_next_schedule(self):
        """
        Returns the next schedule based on the current date as a
        datetime-object.
        """
        self.date = localtime(self.date)
        next_minute = self.get_next_minute()
        if next_minute:
            if self.hour_is_allowed():
                if self.month_is_allowed():
                    return self._get_schedule(minute=next_minute)
        return self.get_schedule_next_hour()

    def get_schedule_next_hour(self):
        """
        Returns the next schedule as a datetime-object.
        The first minute is valid, the next hour has to be found.
        """
        first_minute = self.get_first_minute()
        next_hour = self.get_next_hour()
        if next_hour:
            if self.day_is_allowed():
                if self.month_is_allowed():
                    schedule = self._get_schedule(
                        hour=next_hour, minute=first_minute)
                else:
                    first_hour = self.get_first_hour()
                    schedule = self.get_schedule_next_month(
                        hour=first_hour, minute=first_minute)
                return schedule
        return self.get_schedule_next_day(first_minute)

    def get_schedule_next_day(self, minute):
        """
        Returns the next schedule as a datetime-object.
        The first minute is valid, the next hour has to be found.
        """
        first_hour = self.get_first_hour()
        next_day = self.get_next_day()
        if next_day:
            if self.month_is_allowed():
                return self._get_schedule(
                    day=next_day, hour=first_hour, minute=minute)
        return self.get_schedule_next_month(first_hour, minute)

    def get_schedule_next_month(self, hour, minute):
        """
        Returns the next schedule as a datetime-object.
        The first minute and hour are valid, the next day has to be
        found.
        """
        year, month = self.get_next_month()
        day = self.get_first_day(year, month)
        schedule = self._get_schedule(
            year=year, month=month, day=day, hour=hour, minute=minute)
        return schedule

    def hour_is_allowed(self):
        """
        Returns a boolean whether the current hour is allowed for the
        current date.
        """
        if self.hours:
            return self.date.hour in self.hours
        # else: every hour is allowed
        return True

    def day_is_allowed(self):
        """
        Returns a boolean whether the current day is allowed for the
        current date.
        """
        if not self.dow and not self.dom:
            # every day is alloed:
            return True
        if self.date.day in self.dom:
            return True
        # now check whether day of week is allowed
        this = self.date
        weekday = calendar.weekday(this.year, this.month, this.day)
        return weekday in self.dow

    def month_is_allowed(self):
        """
        Returns a boolean whether the current month is allowed for the
        current date.
        """
        if self.months:
            return self.date.month in self.months
        # else: every month is allowed
        return True

    def get_first_minute(self):
        """Returns the first allowed minute of an hour."""
        return self.minutes[0] if self.minutes else 0

    def get_first_hour(self):
        """Returns the first allowed hour of a day."""
        return self.hours[0] if self.hours else 0

    def get_first_day(self, year, month):
        """Returns the first allowed day of the given month and year."""
        if not (self.dow or self.dom):
            # every day is allowed
            return 1
        first_dom_day = self.dom[0] if self.dom else None
        first_dow_day = None
        if self.dow:
            first_weekday, _ = calendar.monthrange(year, month)
            if first_weekday in self.dow:
                return 1
            first_allowed_weekday = get_next_value(first_weekday, self.dow)
            if first_allowed_weekday:
                delta = first_allowed_weekday - first_weekday
            else:
                delta = first_weekday - self.dow[0]
                if delta > 0:
                    delta = 7 - delta
            first_dow_day = 1 + delta
        if first_dow_day and first_dom_day:
            return min(first_dom_day, first_dow_day)
        return first_dom_day or first_dow_day

    def get_next_minute(self):
        """
        Returns next allowed minute according to self.date.
        Returns None if no next allowed minute can be found.
        """
        if self.minutes:
            return get_next_value(self.date.minute, self.minutes)
        return self.date.minute + 1 if self.date.minute < 59 else None

    def get_next_hour(self):
        """
        Returns next allowed hour according to self.date.
        Returns None if no next allowed hour can be found.
        """
        if self.hours:
            return get_next_value(self.date.hour, self.hours)
        return self.date.hour + 1 if self.date.hour < 23 else None

    def get_next_day(self):
        """
        Returns next allowed day according to self.date.
        Returns None if no next allowed day can be found.
        """
        _, max_days = calendar.monthrange(
            self.date.year, self.date.month)
        if not self.dow and not self.dom:
            next_day = self.date.day + 1
        else:
            next_dom_day = None
            next_dow_day = None
            if self.dom:
                next_dom_day = get_next_value(self.date.day, self.dom)
            if self.dow:
                weekday = self.date.weekday()
                next_weekday = get_next_value(weekday, self.dow) or self.dow[0]
                delta_days = next_weekday - weekday
                if delta_days <= 0:
                    delta_days += 7
                next_dow_day = self.date.day + delta_days
            if next_dom_day and next_dow_day:
                next_day = min(next_dom_day, next_dow_day)
            else:
                next_day = next_dom_day or next_dow_day
        if next_day and next_day > max_days:
            next_day = None
        return next_day

    def get_next_month(self):
        """
        Returns next allowed tuple of (month, year) according to
        self.date.
        """
        year = self.date.year
        if self.months:
            # just selective months are allowed
            next_month = get_next_value(self.date.month, self.months)
            if next_month is None:
                year += 1
                next_month = get_next_value(0, self.months)
        else:
            # every month is allowed
            next_month = self.date.month + 1
            if next_month > 12:
                next_month = 1
                year += 1
        return year, next_month

    def _get_schedule(self, year=None, month=None,
                      day=None, hour=None, minute=None):
        """
        Returns a datetime-object with the arguments or the values from
        self.date as default.
        """
        year = year or self.date.year
        month = month or self.date.month
        day = day or self.date.day
        # hour and minute are allowed to be 0, therefore test for None
        hour = hour if hour is not None else self.date.hour
        minute = minute if minute is not None else self.date.minute
        schedule = datetime.datetime(year, month, day, hour, minute)
        if settings.USE_TZ:
            schedule = make_aware(schedule)
        return schedule


def get_next_value(start_value, values):
    """
    Returns next value from a sequence of values if there is a value >
    start_value. Returns None if no such value is found.
    """
    if values is not None:
        for value in values:
            if value > start_value:
                return value
    return None
