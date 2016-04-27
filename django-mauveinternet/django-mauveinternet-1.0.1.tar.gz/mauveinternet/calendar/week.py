import datetime

class Week(object):
    def __init__(self, year, weeknum):
        self.year = year
        self.weeknum = weeknum

    def day(self, off):
        """Weeks are numbered from the week containing the fourth of January

        >>> Week(2009, 01).monday()
        datetime.date(2008, 12, 29)
        >>> Week(2008, 04).monday()
        datetime.date(2008, 1, 21)
        """
        fourth = datetime.date(self.year, 1, 4)
        w01 = fourth - datetime.timedelta(fourth.weekday())
        days = 7 * (self.weeknum - 1) + off
        return w01 + datetime.timedelta(days=days)

    def monday(self):
        return self.day(0)

    def tuesday(self):
        return self.day(1)

    def wednesday(self):
        return self.day(2)

    def thursday(self):
        return self.day(3)

    def friday(self):
        return self.day(4)

    def saturday(self):
        return self.day(5)

    def sunday(self):
        return self.day(6)

    def __repr__(self):
        return 'Week(%r, %r)' % (self.year, self.weeknum)

    def __str__(self):
        return '%04d-W%02d' % (self.year, self.weeknum)

    def __unicode__(self):
        return unicode(str(self))

    def __eq__(self, ano):
        return self.year == ano.year and self.weeknum == ano.weeknum

    def next(self):
        """
        >>> Week(2009, 53).next()
        Week(2010, 1)
        >>> Week(2008, 52).next()
        Week(2009, 1)
        """
        return Week.for_date(self.day(7))

    def prev(self):
        return Week.for_date(self.day(-1))

    @staticmethod
    def for_date(d):
        """Compute the ISO week for a given date.

        >>> Week.for_date(datetime.date(2009, 4, 12))
        Week(2009, 15)
        >>> Week.for_date(datetime.date(2008, 12, 31))
        Week(2009, 1)
        >>> Week.for_date(datetime.date(2010, 1, 3))
        Week(2009, 53)
        >>> Week.for_date(datetime.date(2009, 4, 13))
        Week(2009, 16)
        """
        thursday = d + datetime.timedelta(3 - d.weekday()) # Thursday this week
        first = thursday.replace(month=1, day=1)
        week = (thursday - first).days // 7 + 1
        return Week(thursday.year, week)

    @staticmethod
    def current():
        return Week.for_date(datetime.date.today())


if __name__ == '__main__':
    import doctest
    doctest.testmod()
