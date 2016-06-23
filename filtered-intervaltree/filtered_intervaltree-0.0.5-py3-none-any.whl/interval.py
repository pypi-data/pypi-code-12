from typing import List
from sys import maxsize
from collections import namedtuple


def get_minimum_bounding_interval(interval_a, interval_b) -> 'Interval':
    points = [
        interval_a.begin,
        interval_a.end,
        interval_b.begin,
        interval_b.end,
    ]
    sorted(points)
    return Interval(points[0], points[-1])


def combine_three_intervals(interval_a, interval_b, interval_c):
    points = [
        interval_a.begin,
        interval_a.end,
        interval_b.begin,
        interval_b.end,
        interval_c.begin,
        interval_c.end
    ]
    sorted(points)
    return Interval(points[0], points[-1])


def combine_intervals(interval_a, interval_b: 'Interval') -> 'Interval':
    begin = interval_a.begin if interval_a.begin < interval_b.begin else interval_b.begin
    end = interval_a.end if interval_a.end > interval_b.end else interval_b.end
    return Interval(begin, end)


def interval_contains(interval_a: 'Interval', interval_b: 'Interval') -> bool:
    return interval_a.begin <= interval_b.begin and interval_a.end >= interval_b.end


def interval_overlaps(interval_a: 'Interval', interval_b: 'Interval') -> bool:
    first = interval_a if interval_a <= interval_b else interval_b
    second = interval_b if interval_a is first else interval_a
    return second.end > first.begin and second.begin < first.end


def get_overlap(interval_a: 'Interval', interval_b: 'Interval') -> 'Interval':
    contained = interval_b in interval_a
    if contained:
        return interval_b
    if interval_b.begin <= interval_a.begin:
        begin = interval_a.begin
        end = interval_b.end
        return Interval(begin, end)

    begin = interval_b.begin
    end = interval_a.end
    return Interval(begin, end)


class Interval(namedtuple('Interval', ['begin', 'end'])):
    __slots__ = ()

    def __new__(cls, begin=0, end=maxsize):
        self = super(Interval, cls).__new__(cls, begin, end)
        return self

    def __lt__(self, other: 'Interval'):
        return self.begin < other.begin

    def __le__(self, other: 'Interval'):
        return self.begin <= other.begin

    def __gt__(self, other: 'Interval'):
        return self.begin > other.begin

    def __ge__(self, other: 'Interval'):
        return self.begin >= other.begin

    def __contains__(self, item: 'Interval'):
        return interval_contains(self, item)

    def __len__(self):
        return self.end - self.begin

    def __add__(self, other: 'Interval') -> 'Interval':
        begin = self.begin if self.begin < other.begin else other.begin
        end = self.end if self.end > other.end else other.end
        return Interval(begin, end)

    def overlaps(self, other: 'Interval') -> bool:
        return interval_overlaps(self, other)

    def touches(self, other: 'Interval') -> bool:
        return self.begin == other.end or self.end == other.begin

    def _get_overlap(self, other: 'Interval') -> 'Interval':
        return get_overlap(self, other)

    def remove(self, other: 'Interval') -> List['Interval']:
        overlaps = self.overlaps(other)
        contained = self in other

        if contained:
            return []

        if overlaps:
            overlap = self._get_overlap(other)
            segments = [
                Interval(self.begin, overlap.begin),
                # overlap,
                Interval(overlap.end, self.end)
            ]

            tmp = filter(lambda x: len(x), segments)
            return list(tmp)
        else:
            return [self]

