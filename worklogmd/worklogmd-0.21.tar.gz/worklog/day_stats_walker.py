from .parsing import WorklogListener
from datetime import datetime


def parse_time(s):
    return datetime.strptime(s, '%H:%M')


def parse_date(s):
    return datetime.strptime(s, '%d %b %Y')


def parse_time_range(s):
    start_str, end_str = s.split('-')
    return parse_time(start_str), parse_time(end_str)


class DayStatsWalker(WorklogListener):
    def __init__(self):
        self.stats = {}
        self._current_stats = None
        self._current_date = None

    def _save_current_stats(self):
        self.stats[self._current_date] = self._current_stats

    def enterDayHeader(self, ctx):
        if self._current_date:
            self._save_current_stats()

        _, day, _, month, _, year = [c.getText() for c in ctx.children]
        self._current_date = parse_date('{} {} {}'.format(day, month, year))
        self._current_stats = {'extra_start': None,
                               'extra_end': None}

    def enterStart(self, ctx):
        _, start_str = [c.getText() for c in ctx.children]
        self._current_stats['start'] = parse_time(start_str)

    def enterLunch(self, ctx):
        tokens = [c.getText() for c in ctx.children]

        self._current_stats['is_lunch_business'] = False
        if len(tokens) > 2 and 'biz' in tokens[2]:
            self._current_stats['is_lunch_business'] = True

        self._current_stats['lunch_start'] = None
        self._current_stats['lunch_end'] = None
        if tokens[1] != 'N/A':
            lunch_start, lunch_end = parse_time_range(tokens[1])
            self._current_stats['lunch_start'] = lunch_start
            self._current_stats['lunch_end'] = lunch_end

    def enterStop(self, ctx):
        _, stop_str = [c.getText() for c in ctx.children]
        self._current_stats['end'] = parse_time(stop_str)

    def enterExtra(self, ctx):
        _, _, time_range = [c.getText() for c in ctx.children]
        extra_start, extra_end = parse_time_range(time_range)
        self._current_stats['extra_start'] = extra_start
        self._current_stats['extra_end'] = extra_end
