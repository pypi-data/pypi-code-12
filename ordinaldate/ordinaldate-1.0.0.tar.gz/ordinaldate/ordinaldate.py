# coding=utf-8
from calendar import Calendar
from datetime import date
from enum import IntEnum


__all__ = [
    "get_by_values",
    "Month",
    "ordinal_date",
    "Ordinal",
    "OrdinalDateError",
    "Weekday"
]


class OrdinalDateError(Exception):
    pass


class Ordinal(IntEnum):
    first = 1
    second = 2
    third = 3
    fourth = 4
    fifth = 5
    last = 6


class Weekday(IntEnum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6


class Month(IntEnum):
    January = 1
    February = 2
    March = 3
    April = 4
    May = 5
    June = 6
    July = 7
    August = 8
    September = 9
    October = 10
    November = 11
    December = 12


def get_by_values(ordinal, target_week_day, month, year=None):
    """
    Returns a `datetime.date` object for a specific ordinal of a month:
    For example the First Tuesday in November is election day:

    election_day = roving_date(Ordinal.first, Weekday.tuesday, Month.november)

    :param ordinal:
    :param target_week_day:
    :param month:
    :param year:
    :return date:
    """

    if month not in [m.value for m in Month]:
        err_msg = "`{}` is not in range 1..12".format(month)
        raise OrdinalDateError(err_msg)

    if target_week_day not in [d.value for d in Weekday]:
        err_msg = "`{}` is not in range 0..6".format(target_week_day)
        raise OrdinalDateError(err_msg)

    if year is None:
        year = date.today().year

    month_days = Calendar().monthdays2calendar(year, month)

    # Filter out any days but the `target_week_day`
    filtered_days = []
    append = filtered_days.append
    for week_days in month_days:
        for month_day, week_day in week_days:
            # `month_day` will be 0 (zero) if the particular day is not
            # within the target month so even though the `week_day` is
            # correct the day should be discarded.
            if month_day and week_day == target_week_day:
                append(month_day)

    if ordinal != Ordinal.last:
        try:
            day = filtered_days[ordinal - 1]
        except IndexError:
            month_name = month.name if isinstance(month, Month) else month
            if isinstance(month_name, int):
                month_name = _get_name_by_value(month_name, Month)
            if hasattr(month_name, 'title'):
                month_name = month_name.title()

            ordinal_value = ordinal.value if isinstance(ordinal, Ordinal) else ordinal

            week_day_name = target_week_day.name if isinstance(target_week_day, Weekday) else target_week_day
            if isinstance(week_day_name, int):
                week_day_name = _get_name_by_value(week_day_name, Weekday)
            if hasattr(week_day_name, 'title'):
                week_day_name = week_day_name.title()

            raise OrdinalDateError(
                "Month `{}` does not have {} {}s in it!".format(
                    month_name,
                    ordinal_value,
                    week_day_name
                )
            )
    else:
        day = filtered_days[-1]

    return date(year, month, day)


def _get_name_by_value(value, enum):
    """
    Gets the Enum member name by its value.
    :param value: The integer value of the member.
    :param enum: Enum object to search.
    :return name:
    """
    for member in enum:
        if member.value == value:
            return member.name


def is_week_end(d):
    """
    Return True|False if the datetime.date object is a Saturday or Sunday
    :param d: datetime.date
    :return True|False:
    """
    weekday = d.isoweekday() - 1
    return weekday == Weekday.Saturday or weekday == Weekday.Sunday


class OrdinalDate:

    def __init__(self):
        pass

    class DayOfWeek:
        def __init__(self, ordinal=None):
            self.ordinal = ordinal

        class Month:
            def __init__(self, ordinal, target_week_day):
                self.ordinal = ordinal
                self.target_week_day = target_week_day

            @property
            def january(self):
                return get_by_values(self.ordinal, self.target_week_day, Month.January)

            @property
            def february(self):
                return get_by_values(self.ordinal, self.target_week_day, Month.February)

            @property
            def march(self):
                return get_by_values(self.ordinal, self.target_week_day, Month.March)

            @property
            def april(self):
                return get_by_values(self.ordinal, self.target_week_day, Month.April)

            @property
            def may(self):
                return get_by_values(self.ordinal, self.target_week_day, Month.May)

            @property
            def june(self):
                return get_by_values(self.ordinal, self.target_week_day, Month.June)

            @property
            def july(self):
                return get_by_values(self.ordinal, self.target_week_day, Month.July)

            @property
            def august(self):
                return get_by_values(self.ordinal, self.target_week_day, Month.August)

            @property
            def september(self):
                return get_by_values(self.ordinal, self.target_week_day, Month.September)

            @property
            def october(self):
                return get_by_values(self.ordinal, self.target_week_day, Month.October)

            @property
            def november(self):
                return get_by_values(self.ordinal, self.target_week_day, Month.November)

            @property
            def december(self):
                return get_by_values(self.ordinal, self.target_week_day, Month.December)

        @property
        def monday(self):
            return self.Month(self.ordinal, Weekday.Monday)

        @property
        def tuesday(self):
            return self.Month(self.ordinal, Weekday.Tuesday)

        @property
        def wednesday(self):
            return self.Month(self.ordinal, Weekday.Wednesday)

        @property
        def thursday(self):
            return self.Month(self.ordinal, Weekday.Thursday)

        @property
        def friday(self):
            return self.Month(self.ordinal, Weekday.Friday)

        @property
        def saturday(self):
            return self.Month(self.ordinal, Weekday.Saturday)

        @property
        def sunday(self):
            return self.Month(self.ordinal, Weekday.Sunday)

    @property
    def first(self):
        return self.DayOfWeek(ordinal=Ordinal.first)

    @property
    def second(self):
        return self.DayOfWeek(ordinal=Ordinal.second)

    @property
    def third(self):
        return self.DayOfWeek(ordinal=Ordinal.third)

    @property
    def fourth(self):
        return self.DayOfWeek(ordinal=Ordinal.fourth)

    @property
    def fifth(self):
        return self.DayOfWeek(ordinal=Ordinal.fifth)

    @property
    def last(self):
        return self.DayOfWeek(ordinal=Ordinal.last)
