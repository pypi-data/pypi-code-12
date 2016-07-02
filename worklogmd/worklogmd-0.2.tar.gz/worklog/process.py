'''
Usage examples:

Process the file worklog.md:

    python process.py worklog.md

(By default, output figure is saved in whatever your filename is appended with
'.png', so 'worklog.md.png' in this case)

Process the file worklog.md, storing output in foo.png:

    python process.py worklog.md foo.png
'''
from .day_stats_walker import DayStatsWalker
from .parsing import WorklogLexer, WorklogParser
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from itertools import groupby
import sys


def sorted_groupby(iterable, key=None):
    return groupby(sorted(iterable, key=key), key=key)


def hours_diff(end, start):
    if not end or not start:
        return 0
    diff = end - start
    return diff.total_seconds() / 3600


def get_hours_per_day(day_to_stats):
    for day, stats in sorted(day_to_stats.items()):
        time_at_lunch = hours_diff(stats['lunch_end'], stats['lunch_start'])
        if stats['is_lunch_business']:
            time_at_lunch = 0
        time_at_office = hours_diff(stats['end'], stats['start'])
        time_at_office += hours_diff(stats['extra_end'], stats['extra_start'])

        yield day, time_at_office - time_at_lunch


def week_of_year(day_hours):
    ic = day_hours[0].isocalendar()
    return ic[0], ic[1]


def get_hours_per_week(day_to_stats):
    for week, day_hours in groupby(get_hours_per_day(day_to_stats),
                                   key=week_of_year):
        yield week, sum([h for _, h in day_hours])


def print_hours_per_day(day_to_stats):
    for day, hours in get_hours_per_day(day_to_stats):
        print(day.strftime('%Y-%m-%d:'), hours)


def print_hours_per_week(day_to_stats):
    for week, hours in get_hours_per_week(day_to_stats):
        print('{}wk{}: {:.02f}'.format(week[0], week[1], hours))

def run():
    daily = True
    try:
        option = sys.argv[2]
        if option == '-w':
            daily = False
    except IndexError:
        pass

    input_file = FileStream(sys.argv[1])
    lexer = WorklogLexer(input_file)
    stream = CommonTokenStream(lexer)
    parser = WorklogParser(stream)
    tree = parser.wl()

    stats_walker = DayStatsWalker()
    walker = ParseTreeWalker()
    walker.walk(stats_walker, tree)
    stats_walker._save_current_stats()

    day_to_stats = stats_walker.stats

    if daily:
        print_hours_per_day(day_to_stats)
    else:
        print_hours_per_week(day_to_stats)

if __name__ == '__main__':
    run()
