import calendar
import datetime


class NamedDateError(Exception):
    pass


class DateLogicError(NamedDateError):
    pass


class NoNthWeekdayError(NamedDateError):
    pass


class MissingArgumentsError(NamedDateError):
    pass


class NamedDatesKeyError(NamedDateError):
    pass


def day_of_nth_weekday(year, month, weekday, **kwargs):
    """Determine the day of the month on which the ``nth`` time ``weekday``
     occurs in ``month`` of ``year``.

    :param year: Year
    :param month: Month
    :param weekday: Integer representing the day of week (0-6, Monday through
        Sunday).
    :param nth: The number occurrence of ``weekday`` in ``month`` of ``year``.
    :param from_end: If True, then ``nth`` looks backwards from the
        end of ``month``of ``year``.
    :return: An integer day of the month.
    :raises NoNthWeekdayException: If no nth weekday exists for this month
        and year.
    """
    nth = kwargs.pop('nth', 1)
    from_end = kwargs.pop('from_end', False)
    if kwargs:
        raise TypeError("Unexpected **kwargs: %r" % kwargs)

    days_in_month = calendar.monthrange(year, month)[1]
    reference_day = 1 if not from_end else days_in_month
    reference_weekday = datetime.date(year, month, reference_day).weekday()

    nth_offset = 7 * (nth - 1)
    if ((not from_end and weekday < reference_weekday) or
            (from_end and weekday > reference_weekday)):
        nth_offset += 7

    if from_end:
        nth_offset = -nth_offset

    day = reference_day + nth_offset + weekday - reference_weekday
    if nth < 1 or not (1 <= day <= days_in_month):
        raise NoNthWeekdayError()

    return day


def make_falls_on(month, day):
    def falls_on(date):
        return date.month == month and date.day == day

    return falls_on


def make_falls_on_nth_weekday(month, day, nth, from_end):
    def falls_on(date):
        nth_weekday = day_of_nth_weekday(date.year, date.month, day,
                                         nth=nth, from_end=from_end)
        return date.month == month and date.day == nth_weekday

    return falls_on


def make_falls_on_nearest_weekday(month, day):
    def falls_on(date):
        if date.month == month and date.day == day:
            return True

        # If the date doesn't match and it's a Friday or Monday,
        # then it may be the weekday nearest to the actual date.
        one_day = datetime.timedelta(days=1)
        if date.weekday() == 0:
            weekday_date = date - one_day
        elif date.weekday() == 4:
            weekday_date = date + one_day
        else:
            return False

        return weekday_date.month == month and weekday_date.day == day

    return falls_on


class NamedDate(object):
    """An object that encapsulates the logic of dates often referenced by name
    instead of date. Many times, this is because the date on which it falls
    varies from year to year."""

    def __init__(self, name, month=None, day=None, **kwargs):
        """
        :param name: The name of the date.
        :param month: Month.
        :param day: If nth is None, represents a specific date of ``month``.
            Otherwise, represents a weekday (0-6, Monday-Sunday).
        :param nth: The number occurrence of ``day`` (as a weekday) in ``month``
            of ``year``.
        :param from_end: Logical. If True, then ``nth`` looks backwards from the
            end of ``month``of ``year``.
        :param or_nearest_weekday: Logical. If True, whenever the named date
            would fall on a weekend, it will also be considered to fall on the
            neighboring Friday or Monday. May not be used with ``nth`` option.
        :param custom_func: A user defined function for determining whether a
            date falls on an input date argument. If provided, all other
            arguments except ``name`` are ignored. The function should
            take the form:
                def my_func(date):
                    return True if date is the named date else False
        :param aliases: A list of alternative names this date can be referenced by.
        """
        nth = kwargs.pop('nth', None)
        from_end = kwargs.pop('from_end', False)
        or_nearest_weekday = kwargs.pop('or_nearest_weekday', False)
        custom_func = kwargs.pop('custom_func', None)
        aliases = kwargs.pop('aliases', [])
        if kwargs:
            raise TypeError("Unexpected **kwargs: %r" % kwargs)

        self._names = [name] + list(aliases)

        # User defined 'falls on' functions cut out early.
        if custom_func:
            self.__falls_on = custom_func
            return

        # Otherwise, build the 'falls on' logic from the construction parameters.
        if (not month) or (day is None):  # Beware, day == 0 is valid
            raise MissingArgumentsError(
                "month and day, or custom_func, must be specified to " +
                "register a date. ")

        if nth and or_nearest_weekday:
            raise DateLogicError(
                "Cannot use nth day and nearest weekday behaviors together.")

        # If this grows, it may be worth refactoring to some creational pattern.
        if nth:
            falls_on_func = make_falls_on_nth_weekday(month, day, nth, from_end)
        elif or_nearest_weekday:
            falls_on_func = make_falls_on_nearest_weekday(month, day)
        else:
            falls_on_func = make_falls_on(month, day)

        self.__falls_on = falls_on_func

    def falls_on(self, date):
        """Does this named date occur on ``date``?"""
        return self.__falls_on(date)

    @property
    def names(self):
        return self._names


class NamedDates(object):
    """An object to represent a set of NamedDates."""

    def __init__(self, named_dates=None):
        if not named_dates:
            named_dates = []

        self.__named_dates = {}
        for named_date in named_dates:
            for name in named_date.names:
                if self.__named_dates.get(name) is not None:
                    raise NamedDatesKeyError(
                        "Conflicting duplicate name '%s' found." % name)
                self.__named_dates[name] = named_date

    def __getitem__(self, name):
        try:
            return self.__named_dates[name]
        except KeyError:
            raise NamedDatesKeyError(name)

    def __len__(self):
        return len(self.__named_dates)
    
    def add(self, named_date):
        for name in named_date.names:
            if self.__named_dates.get(name) is not None:
                raise NamedDatesKeyError(
                    "Conflicting duplicate name '%s' found." % name)
            self.__named_dates[name] = named_date

    def observes(self, date):
        """Does this date fall on any NamedDate in this set?"""
        return any([nd.falls_on(date) for nd in self.__named_dates.values()])

    @property
    def names(self):
        return self.__named_dates.keys()
