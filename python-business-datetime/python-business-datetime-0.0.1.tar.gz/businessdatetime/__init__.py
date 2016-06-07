from datetime import datetime, timedelta


class BusinessDatetime(object):
    """
    Datetime wrapper used for calculating the number of working datetimes between two datetimes
    ex:
    >>> import datetime
    >>> from businessdatetime import BusinessDatetime
    >>> dt = datetime.datetime(2016, 6, 6, 8, 30)
    >>> bdt = BusinessDatetime(dt)
    >>> print bdt  # Outputs 2016-06-06 8:30:00
    >>> bdt = BusinessDatetime(dt, working_hours=(9, 17))  # Working hours from 9am to 5pm
    >>> print bdt  # Outputs 2016-06-05 16:30:00

    """

    def __init__(self, dt, working_hours=(8.5, 17), working_days=(0, 1, 2, 3, 4), holidays=None):
        """

        :param dt: datetime object
        :param working_hours: number representation of the start and end working hours. (8.5 = 8:30 AM)
        :param working_days: tuple representing the days of the week which are working days. 0 = Monday, 6 = Sunday
        :param holidays: A list of datetime objects representing holidays (not implemented)
        """
        self.original_datetime = dt
        self.holidays = holidays
        self.working_hours = self._start_working_hour, self._end_working_hour = working_hours
        self.start_working_hour, self.start_working_minute = divmod(self._start_working_hour * 60, 60)
        self.start_working_hour = int(self.start_working_hour)
        self.start_working_minute = int(self.start_working_minute)
        self.end_working_hour, self.end_working_minute = divmod(self._end_working_hour * 60, 60)
        self.end_working_hour = int(self.end_working_hour)
        self.end_working_minute = int(self.end_working_minute)
        self.working_days = working_days

        # The end of the current working day supplied by the dt param
        self.current_work_day_end = datetime(dt.year, dt.month, dt.day, self.end_working_hour, self.end_working_minute)

        # The beginning of the current working day supplied by the dt param
        self.current_work_day_start = datetime(dt.year, dt.month, dt.day, self.start_working_hour,
                                               self.start_working_minute)

    def __str__(self):
        return str(self.business_datetime)

    def __repr__(self):
        return repr(self.business_datetime)

    def __sub__(self, other):
        if isinstance(other, timedelta):
            return BusinessDatetime(self.business_datetime - other)
        elif isinstance(other, datetime):
            other = BusinessDatetime(other)
        elif isinstance(other, BusinessDatetime):
            pass
        else:
            raise TypeError("unsupported operand type(s) for -: '%s' and '%s'" % (
            other.__class__.__name__, self.__class__.__name__))
        return self.calc_diff(other)

    def calc_diff(self, other):
        lesser_time_total_seconds = other.remaining_time().total_seconds()
        greater_time_total_seconds = self.passed_time().total_seconds()
        seconds_in_workday = (self.current_work_day_end - self.current_work_day_start).total_seconds()
        day_difference = 0
        dont_count_days = 0
        d = other.business_datetime
        while d.day != self.business_datetime.day:
            d += timedelta(days=1)
            # ToDo: Check if weekday is in holidays and increment dont_count_days
            if d.weekday() not in self.working_days:
                dont_count_days += 1
            day_difference += 1
        number_of_non_working_days = day_difference - 1 - dont_count_days
        non_working_days_seconds = number_of_non_working_days * seconds_in_workday
        working_days_seconds = lesser_time_total_seconds + greater_time_total_seconds
        total_seconds_between_time_stamps = working_days_seconds + non_working_days_seconds
        return timedelta(seconds=total_seconds_between_time_stamps)

    def out_of_bounds(self):
        """
        Return whether or not the original timestamp is out of valid working hours.
        :return:
        """
        return self.original_datetime > self.current_work_day_end or self.original_datetime < self.current_work_day_start

    @property
    def business_datetime(self):
        """
        Return the business datetime for the original timestamp.
        :return:
        """
        if self.original_datetime > self.current_work_day_end:
            return self.rollforward()
        elif self.original_datetime < self.current_work_day_start:
            return self.rollback()
        else:
            return self.original_datetime

    @property
    def next_business_day_start(self):
        """
        datetime object representing the next business days start time.
        :rtype: datetime
        :return:
        """
        d = datetime(self.original_datetime.year, self.original_datetime.month, self.original_datetime.day,
                     self.start_working_hour, self.start_working_minute) + timedelta(days=1)
        while d.weekday() not in self.working_days:
            d += timedelta(days=1)
        return d

    @property
    def previous_business_day_end(self):
        """
        datetime object representing the previous business days end time.
        :rtype: datetime
        :return:
        """
        d = datetime(self.original_datetime.year, self.original_datetime.month, self.original_datetime.day,
                     self.end_working_hour, self.end_working_minute) - timedelta(days=1)
        while d.weekday() not in self.working_days:
            d -= timedelta(days=1)
        return d

    def remaining_time(self):
        """
        Return a timedelta with the remaining time left in the work day
        :return:
        """
        return self.current_work_day_end - self.business_datetime

    def passed_time(self):
        """
        Return a timedelta with the amount of time that has passed since the beginning of the day to the current time
        :return:
        """
        return self.business_datetime - self.current_work_day_start

    def rollforward(self):
        """
        Return a datetime object which falls within working hours with the starting offset equal to the amount
        of time that the original datetime object exceeds the end working hour.

        ex.
            >>> # The following datetime exceeds the working day by 30 seconds.
            >>> example_dt = datetime(2016, 6, 6, 17, 0, 30)  # 2016-06-05 5:00:30 PM
            >>> example_bdt = BusinessDatetime(example_dt)
            >>> print example_bdt.rollforward()
            2016-06-06 8:30:30
        :return:
        """
        overflow = datetime(self.original_datetime.year, self.original_datetime.month, self.original_datetime.day,
                            self.end_working_hour, self.end_working_minute)
        td = self.original_datetime - overflow
        return self.next_business_day_start + td

    def rollback(self):
        """
        Return a datetime object which falls within working hours with the ending offset equal to the amount
        of time that the original datetime object falls short of the start working hour.

        ex.
            >>> # The following datetime preceeds the working day by 1 minute.
            >>> example_dt = datetime(2016, 6, 6, 8, 29)  # 2016-06-05 8:29:00 AM
            >>> example_bdt = BusinessDatetime(example_dt)
            >>> print example_bdt.rollback()
            2016-06-04 16:59:00
        :return:
        """
        underflow = datetime(self.original_datetime.year, self.original_datetime.month, self.original_datetime.day,
                             self.start_working_hour, self.start_working_minute)
        td = underflow - self.original_datetime
        return self.previous_business_day_end - td


class BusinessDatetimeCalculator(object):
    def __init__(self, working_hours=(8.5, 17), working_days=(0, 1, 2, 3, 4), holidays=None):
        """

        :param dt: datetime object
        :param working_hours: number representation of the start and end working hours. (8.5 = 8:30 AM)
        :param working_days: tuple representing the days of the week which are working days. 0 = Monday, 6 = Sunday
        :param holidays: A list of datetime objects representing holidays (not implemented)
        """
        self.holidays = holidays
        self.working_hours = self._start_working_hour, self._end_working_hour = working_hours
        self.start_working_hour, self.start_working_minute = divmod(self._start_working_hour * 60, 60)
        self.start_working_hour = int(self.start_working_hour)
        self.start_working_minute = int(self.start_working_minute)
        self.end_working_hour, self.end_working_minute = divmod(self._end_working_hour * 60, 60)
        self.end_working_hour = int(self.end_working_hour)
        self.end_working_minute = int(self.end_working_minute)
        self.working_days = working_days

    def get_work_day_end(self, dt):
        # The end of the current working day supplied by the dt param
        return datetime(dt.year, dt.month, dt.day, self.end_working_hour, self.end_working_minute)

    def get_work_day_start(self, dt):
        # The beginning of the current working day supplied by the dt param
        return datetime(dt.year, dt.month, dt.day, self.start_working_hour,
                        self.start_working_minute)

    def remaining_time(self, dt):
        """
        Return a timedelta with the remaining time left in the work day
        :return:
        """
        return self.get_work_day_end(dt) - dt

    def passed_time(self, dt):
        """
        Return a timedelta with the amount of time that has passed since the beginning of the day to the current time
        :return:
        """
        return dt - self.get_work_day_start(dt)

    def subtract(self, d1, d2):
        lesser_date = min(d1, d2)
        greater_date = max(d1, d2)
        lesser_time_total_seconds = self.remaining_time(lesser_date).total_seconds()
        greater_time_total_seconds = self.passed_time(greater_date).total_seconds()
        seconds_in_workday = ((self.end_working_hour*60 + self.end_working_minute)*60) - ((self.start_working_hour*60 + self.start_working_minute)*60)
        day_difference = 0
        dont_count_days = 0
        d = lesser_date
        while d.day != greater_date.day:
            d += timedelta(days=1)
            # ToDo: Check if weekday is in holidays and increment dont_count_days
            if d.weekday() not in self.working_days:
                dont_count_days += 1
            day_difference += 1
        number_of_non_working_days = day_difference - 1 - dont_count_days
        non_working_days_seconds = number_of_non_working_days * seconds_in_workday
        working_days_seconds = lesser_time_total_seconds + greater_time_total_seconds
        total_seconds_between_time_stamps = working_days_seconds + non_working_days_seconds
        return timedelta(seconds=total_seconds_between_time_stamps)


def usage_examples():
    dt = datetime(2016, 6, 6, 8, 30)
    bdt = BusinessDatetime(dt)
    print "Example 1:", bdt  # Outputs 2016-06-06 8:30:00
    bdt = BusinessDatetime(dt, working_hours=(9, 17))  # Working hours from 9am to 5pm
    # The reason for the rollback is
    print "Example 2:", bdt  # Outputs 2016-06-05 16:30:00

    # This date falls on a weekend and since it also starts 30 minutes earlier than the starting work hour,
    # it will be rolled back to friday at 4:30 PM so that when subtracting, it can accurately calculate how man
    # working hours are between the other date.
    dt2 = datetime(2016, 6, 4, 8, 30)
    bdt2 = BusinessDatetime(dt2, working_hours=(9, 17))
    print "Example 3:", bdt2

    print bdt - bdt2

    bdtc = BusinessDatetimeCalculator()
    print bdtc.subtract(dt, dt2)
    print bdtc.subtract(dt, datetime(2016, 6, 6, 9, 45, 27))


if __name__ == '__main__':
    usage_examples()
