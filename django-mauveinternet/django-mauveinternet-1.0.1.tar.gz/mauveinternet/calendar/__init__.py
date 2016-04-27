import datetime
from cStringIO import StringIO

from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from month import Month


class PeriodConsumer(object):
    """Stream-based interface for rendering of date-based calendar data.

    Subclasses can hook whichever of these methods they like to output the calendar.
    Note that the dates given with the start and end of a period are not the actual parameters
    of the period because they may have been filtered or adjusted for display.
    """
    def start_month(self, month):
        """Called before the first day of the month, and before any periods in that month."""

    def end_month(self, month):
        """Called after the last day of the month, and after any periods in that month."""

    def start_day(self, date):
        """Called once for each day to display"""

    def start_period(self, date, period):
        """Called before the day in which the period begins"""

    def end_period(self, date, period):
        """Ends the previously started period."""

    def finish(self):
        """Signals to the consumer to expect no more events. This can be used to
        finalize any open events, etc."""


class PeriodFilter(object):
    """Default implementations of all consumer methods to simplify the implementation
    of consumers that only wish to handle some events and pass others through."""
    def __init__(self, consumer=None):
        if consumer is None:
            self.consumer = PeriodConsumer()
        else:
            self.consumer = consumer

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__name

        def _pass_to_consumer(*args, **kwargs):
            return getattr(self.consumer, name)(*args, **kwargs)
        return _pass_to_consumer


class DebugRenderer(PeriodFilter):
    def start_month(self, month):
        print "start_month:", month
        self.consumer.start_month(month)

    def end_month(self, month):
        print "end_month:", month
        self.consumer.end_month(month)

    def start_day(self, date):
        print "day:", date
        self.consumer.start_day(date)

    def start_period(self, date, period):
        print "start of", period, ":", date
        self.consumer.start_period(date, period)

    def end_period(self, date, period):
        print "end of", period, ":", date
        self.consumer.end_period(date, period)

    def finish(self):
        print "finish."
        self.consumer.finish()



class PeriodSource(object):
    """A source of period data from a Django queryset. Emits one signal
    for each instance of a model with a date field, in date order."""

    def __init__(self, queryset, date_field, signal):
        self.queryset = queryset
        self.active_queryset = queryset
        self.date_field = date_field
        self.signal = signal

    def seek(self, date):
        self.active_queryset = queryset.filter(**{self.date_field + '__gte': date})

    def __iter__(self):
        for inst in self.active_queryset.order_by(self.date_field):
            yield self.signal, getattr(inst, self.date_field), inst


class peekable_iter(object):
    """This class wraps an iterator to add the ability to peek
    the next element without consuming it."""
    def __init__(self, it):
        self.it = iter(it)
        self.top = None

    def __iter__(self):
        return self

    def peek(self):
        if self.top is None and self.it:
            try:
                self.top = self.it.next()
            except StopIteration:
                self.top = None
                self.it = None
        return self.top

    def __cmp__(self, ano):
        return cmp(self.peek(), ano.peek())

    def next(self):
        n = self.peek()
        self.top = None
        return n

try:
    from heapq import merge as heapmerge
except ImportError:
    import heapq
    def heapmerge(*iterators):
        heap = [peekable_iter(i) for i in iterators]
        heap = [i for i in heap if i.peek() is not None]
        heapq.heapify(heap)
        try:
            while True:
                yield heap[0].next()
                if heap[0].peek() is None:
                    heapq.heappop(heap)
                else:
                    heapq.heapreplace(heap, heap[0])
        except IndexError:
            """Heap underflow, so stop"""
            pass


class EventMux(object):
    class Event(object):
        def __init__(self, date, obj, signal, priority):
            self.date = date
            self.obj = obj
            self.signal = signal
            self.priority = priority

        def __cmp__(self, ano):
            """Compare events. Earlier events obviously come first, and ties are broken by priority"""
            return cmp(self.date, ano.date) or cmp(self.priority, ano.priority)

        def dispatch(self, consumer):
            getattr(consumer, self.signal)(self.date, self.obj)


    def __init__(self):
        self.sources = []
        self.signal_priorities = {
                'end_period': 10
        }

    def add_source(self, source):
        self.sources.append(source)

    def set_priority(self, signal, priority=0):
        if not priority:
            if signal in self.signal_priorities:
                del(self.signal_priorities)
        else:
            self.signal_priorities[signal] = priority

    def get_priority(self, signal):
        return self.signal_priorities.get(signal, 0)

    def seek(self, date):
        for s in self.sources:
            s.seek(date)

    def iterators(self):
        def eiter(s):
            for signal, date, obj in s:
                priority = self.get_priority(signal)
                yield date, priority, signal, obj

        return [eiter(s) for s in self.sources]

    def __iter__(self):
        if len(self.sources) == 1:
            # avoid heap for degenerate case
            for i in self.sources[0]:
                yield i
        else:
            for date, priority, signal, obj in heapmerge(*self.iterators()):
                yield signal, date, obj


class EventDispatcher(EventMux):
    def feed_to(self, consumer, until=None):
        for signal, date, obj in self:
            if until and date > until:
                break
            getattr(consumer, signal)(date, obj)
        consumer.finish()


class DebugConsumer(object):
    def __getattr__(self, signal):
        def _print_signal(date, obj):
            print u'[%s] %s: %s' % (date, signal, obj)
        return _print_signal


class DateRangeFilter(PeriodFilter):
    """Modifies period starts/ends so that they fit into the
    date range given, issuing start and end signals as appropriate to
    give state."""
    def __init__(self, consumer, start, end):
        self.consumer = consumer
        self.periods = []
        self.start = start
        self.end = end
        self.started = False
        self.finished = False

    def start_period(self, date, period):
        if date >= self.end:
            self.close_all()
            return
        if date >= self.start:
            self.open_all()
            self.consumer.start_period(date, period)
        self.periods.append(period)

    def end_period(self, date, period):
        if date >= self.end:
            self.close_all()
            return
        if date >= self.start:
            self.open_all()
            self.consumer.end_period(date, period)
        self.periods.remove(period)

    def open_all(self):
        if self.started:
            return
        for p in self.periods:
            self.consumer.start_period(self.start, p)
        self.started = True

    def close_all(self):
        if self.finished:
            return
        # issue end events for all open periods in reverse order
        self.periods.reverse()
        for p in self.periods:
            self.consumer.end_period(self.end, p)
        self.finished = True


class MonthAdapter(PeriodFilter):
    def __init__(self, consumer, start_month=None, months=None):
        self.consumer = consumer
        self.date = None # this is the next date to output
        self.month = start_month
        self.months = months
        self.months_started = 0

        if start_month:
            self.consumer.start_month(start_month)
            self.months_started = 1

    def is_last_month(self):
        return self.months is not None and self.months_started >= self.months

    def run_to(self, date, include_month_end):
        """Output all days before this date"""
        if self.date == date:
            return
        if self.month is None:
            if self.is_last_month():
                return
            self.month = Month.for_date(date)
            self.consumer.start_month(self.month)
            self.months_started += 1

        while self.date is None or self.date < (date - datetime.timedelta(days=1)):
            for d in self.month.days():
                if self.date is not None and d <= self.date:
                    continue
                if d == date:
                    break
                self.consumer.start_day(d)
                self.date = d
            else:
                if not include_month_end and self.month.next().first_day() == date:
                    return
                self.consumer.end_month(self.month)
                if self.is_last_month():
                    self.month = None
                    return
                self.month = self.month.next()
                self.consumer.start_month(self.month)
                self.months_started += 1

    def start_period(self, date, period):
        self.run_to(date, include_month_end=True)
        self.consumer.start_period(date, period)

    def end_period(self, date, period):
        self.run_to(date, include_month_end=False)
        self.consumer.end_period(date, period)

    def finish(self):
        if not self.months and self.month:
            self.run_to(self.month.next().last_day(), include_month_end=True)
        elif self.months:
            while self.month:
                self.run_to(self.month.next().last_day(), include_month_end=True)
        self.consumer.finish()


class PeriodMonthSplitter(PeriodFilter):
    """Splits periods across month boundaries"""
    def __init__(self, consumer):
        self.consumer = consumer
        self.periods = []

    def start_period(self, date, period):
        self.consumer.start_period(date, period)
        self.periods.append(period)

    def end_period(self, date, period):
        self.consumer.end_period(date, period)
        self.periods.remove(period)

    def start_month(self, month):
        self.consumer.start_month(month)
        for p in self.periods:
            self.consumer.start_period(month.first_day(), p)

    def end_month(self, month):
        ps = self.periods[:]
        ps.reverse()
        for p in ps:
            self.consumer.end_period(month.next().first_day(), p)
        self.consumer.end_month(month)


class MonthCalendarFacade(DateRangeFilter):
    """Combines the DateRangeFilter and MonthAdapter to produce a calendar from a given date for a fixed number of months.
    DateRangeFilter imposes an earliest and latest period;
    MonthAdapter adds the month and day events and needs the earliest and latest month to show.
    """
    def __init__(self, consumer, start_date=None, months=12):
        if start_date is None:
            start_date = datetime.date.today()
        start_month = Month.for_date(start_date)
        ms = MonthAdapter(PeriodMonthSplitter(consumer), start_month, months)
        super(MonthCalendarFacade, self).__init__(ms, start=start_date, end=start_month.add(months).first_day())


class MonthCalendar(object):
    """Renders a list of periods to a PeriodConsumer, such that periods are broken
    over month boundaries.

    In practice this is a first stab at this class. It can be done much more simply just
    as one class that passes events to a PeriodRenderer, and a PeriodRenderer that
    simply filters the events to split them over month boundaries.
    """
    def __init__(self, periods, start_month, months):
        self.months = [start_month]
        month = start_month
        for m in range(months-1):
            month = month.next()
            self.months.append(month)

        self._divide_periods(periods)

    def _divide_periods(self, periods):
        self.periods = {}
        for m in self.months:
            ps = []
            first = m.first_day()
            last = m.last_day()
            for start, end, period in periods:
                if start <= last and end >= first:
                    print start, end, last, first
                    ps.append((start, end, period))
            self.periods[m] = ps

    def render(self, period_renderer):
        for m in self.months:
            period_renderer.start_month(m)
            ps = self.periods[m][:]
            try:
                start, end, period = ps.pop(0)
            except IndexError:
                start, end, period = [None] * 3
            else:
                if start < m.first_day():
                    period_renderer.start_period(start, period)

            for d in m.days():
                if period and d == end:
                    period_renderer.end_period(end, period)
                    try:
                        start, end, period = ps.pop(0)
                    except IndexError:
                        start, end, period = [None] * 3

                if period and d == start:
                    period_renderer.start_period(start, period)
                period_renderer.start_day(d)
            if period:
                period_renderer.end_period(end, period)
            period_renderer.end_month(m)


class MonthRenderer(PeriodConsumer):
    def __init__(self):
        self.buf = StringIO()

    def start_month(self, month):
        print >>self.buf, """<div class="month">
                <h4>%s</h4>
                <img class="week" src="/assets/cal/week.png" alt=""/>""" % month.name()

        w = month.first_day().weekday()
        if w:
            print >>self.buf, '<div class="padding" style="width: %dpx"></div>' % (w * 21)

    def end_month(self, month):
        print >>self.buf, "</div>"

    def start_day(self, date):
        print >>self.buf, '<span class="day">%d</span>' % date.day


class TextMonthRenderer(PeriodConsumer):
    """Renders the calendar to a string, showing periods in
    bold using ANSI colour codes"""
    def __init__(self):
        self.buf = StringIO()

    def start_month(self, month):
        self.buf.write(month.name().rjust(20))
        w = month.first_day().weekday()
        self.buf.write('\n M  T  W  T  F  S  S')
        self.buf.write('\n--------------------')
        self.buf.write('\n' + '   ' * w)

    def end_month(self, month):
        self.buf.write('\n\n')

    def start_day(self, date):
        self.buf.write('%2d ' % date.day)
        if date.weekday() == 6:
            self.buf.write('\n')

    def finish(self):
        print self.buf.getvalue()


class CLIMonthRenderer(TextMonthRenderer):
    def __init__(self):
        super(CLIMonthRenderer, self).__init__()
        self.ps = 0

    def set_bold(self, bold):
        if bold:
            self.buf.write('\x1B[1m')
        else:
            self.buf.write('\x1B[22m')

    def start_period(self, date, period):
        if not self.ps:
            self.set_bold(True)
        self.ps += 1

    def end_period(self, date, period):
        self.ps -= 1
        if not self.ps:
            self.set_bold(False)

    def start_month(self, month):
        super(CLIMonthRenderer, self).start_month(month)
        if self.ps:
            self.set_bold(True)

    def end_month(self, month):
        if self.ps:
            self.set_bold(False)
        super(CLIMonthRenderer, self).end_month(month)


class PeriodClassifyingRenderer(MonthRenderer):
    def __init__(self, f=None):
        super(PeriodClassifyingRenderer, self).__init__()
        self.period = None
        self.lstatus = self.default_class()
        self.status = self.lstatus
        self.today = datetime.date.today()
        if f is None:
            self.buf = StringIO()
        else:
            self.buf = f

    def default_class(self):
        """Returns a class"""
        raise NotImplementedError()

    def class_for_period(self, period):
        """Returns a tuple (link, class_list)"""
        raise NotImplementedError()

    def start_period(self, date, period):
        link, classes = self.class_for_period(period)

        print >>self.buf, '<a href="%s">' % conditional_escape(link)
        if period == self.period:
            if self.lstatus in classes:
                self.status = self.lstatus
            else:
                self.status = classes[0]
        else:
            if self.lstatus in classes:
                self.status = classes[(classes.index(self.lstatus) + 1) % len(classes)]
            else:
                self.status = classes[0]
        self.period = period

    def end_period(self, date, period):
        print >>self.buf, '</a>'
        self.status = self.default_class()

    def start_day(self, date):
        if date < self.today:
            print >>self.buf, '<span class="day p">%d</span>' % (date.day)
        else:
            print >>self.buf, '<span class="day %s%s">%d</span>' % (self.lstatus, self.status, date.day)
        self.lstatus = self.status
