import datetime

def add_calendar_months(date, months):
    """Adds or subtracts a given number of calendar months from a date or datetime.

    >>> add_calendar_months(datetime.date(2008, 2, 13), 5)
    datetime.date(2008, 7, 13)

    >>> add_calendar_months(datetime.datetime(2008, 2, 29, 12, 37), 12)
    datetime.datetime(2009, 3, 1, 12, 37)
    """

    dy=months//12
    if months < 0:
        dm=months%-12
    else:
        dm=months%12

    try:
        return date.replace(year=date.year+dy, month=date.month+dm)
    except ValueError:
        return date.replace(year=date.year+dy, month=date.month+dm+1, day=1)

class Month(object):
    """Represents a calendar month to allow for simpler calendar
    generation."""
    def __init__(self, year, month):
        self.year=year
        if month not in range(1, 13):
            raise ValueError("month must be in 1-12")
        self.month=month

    def __repr__(self):
        return 'Month(%d, %d)'%(self.year, self.month)

    def __str__(self):
        return '%04d-%02d'%(self.year, self.month)

    def __cmp__(self, ano):
        return cmp((self.year, self.month), (ano.year, ano.month))

    def __hash__(self):
        return hash(('Month', self.year, self.month))

    def __len__(self):
        """Gives the number of days in the month.

        This allows Month to behave like a sequence."""
        if self.month == 2:
            if self.year % 4 != 0:
                return 28
            elif self.year % 100 != 0:
                return 29
            elif self.year % 400 != 0:
                return 28
            return 29
        return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][self.month]

    def __iter__(self):
        """Return an iterator over the days of the month.

        This allows Month to behave like a sequence."""
        return iter(self.days())

    @staticmethod
    def from_date(date):
        """The calendar month in which a given date or datetime falls."""
        return Month(date.year, date.month)

    for_date = from_date # for_date seems more natural to me right now

    @staticmethod
    def now():
        """The current month"""
        return Month.from_date(datetime.date.today())

    def next(self):
        if self.month == 12:
            return Month(self.year+1, 1)
        return Month(self.year, self.month+1)

    def previous(self):
        if self.month == 1:
            return Month(self.year-1, 12)
        return Month(self.year, self.month-1)

    def first_day(self):
        """The first day of the calendar month.

        >>> Month(2009, 3).first_day()
        datetime.date(2009, 3, 1)
        """
        return datetime.date(self.year, self.month, 1)

    def last_day(self):
        """The last day of the calendar month.

        >>> Month(2009, 3).last_day()
        datetime.date(2009, 3, 31)
        >>> Month(2009, 2).last_day()
        datetime.date(2009, 2, 28)
        >>> Month(2008, 2).last_day()
        datetime.date(2008, 2, 29)
        >>> Month(2000, 2).last_day()
        datetime.date(2000, 2, 29)
        >>> Month(2100, 2).last_day()
        datetime.date(2100, 2, 28)
        """
        return datetime.date(self.year, self.month, len(self))

    def days(self):
        return [datetime.date(self.year, self.month, i) for i in range(1, len(self) + 1)]

    def month_name(self):
        return self.first_day().strftime('%B')

    def name(self):
        return self.first_day().strftime('%B %Y')

    def add(self, months):
        """Adds or subtracts a given number of months.

        >>> Month(2009, 3).add(-15)
        Month(2007, 12)
        >>> Month(2009, 3).add(5)
        Month(2009, 8)
        >>> Month(2009, 3).add(25)
        Month(2011, 4)
        >>> Month(2009, 3).add(-14)
        Month(2008, 1)
        """
        # January is 1, not 0, so we have to subtract 1 before calculating
        ms = (self.month - 1) + months
        dy = ms // 12
        # and add it back on afterwards
        m = (ms % 12) + 1

        return Month(year=(self.year + dy), month=m)

    def as_html(self):

        s="""<div class="month">
                <h4>%s</h4>
                <img class="week" src="/assets/cal/week.png" alt=""/>"""%self.name()

        w=self.first_day().weekday()

        if w:
            s+='<div class="padding" style="width: %dpx"></div>'%(w*21)

        for d in self.days():
            s+=self.day_as_html(d)

        s+="""</div>"""

        return mark_safe(s)

    def day_as_html(self, day):
        return mark_safe('<span class="day">%d</span>' % day.day)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
