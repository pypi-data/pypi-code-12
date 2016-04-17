
from datetime import datetime as dt
import pytest

from django.conf import settings
from django.utils.timezone import (
    localtime,
    make_aware,
    now,
)

from autotask.cron import (
    CronScheduler,
    get_next_value,
)

@pytest.mark.parametrize(
    'value, values, result', [
        (None, None, None),
        (0, None, None),
        (0, [], None),
        (0, [0, 3, 5], 3),
        (2, [0, 3, 5], 3),
        (3, [0, 3, 5], 5),
        (5, [0, 3, 5], None),
        (6, [0, 3, 5], None),
    ])
def test_get_next_value(value, values, result):
    assert result == get_next_value(value, values)


@pytest.mark.parametrize(
    'minute, minutes, result', [
        (1, None, 2),
        (58, None, 59),
        (59, None, None),
        (1, [5, 10], 5),
        (5, [5, 10], 10),
        (6, [5, 10], 10),
        (10, [5, 10], None),
        (11, [5, 10], None),
    ])
def test_get_next_minute(minute, minutes, result):
    ls = dt(2016, 3, 27, minute=minute)
    cs = CronScheduler(last_schedule=ls, minutes=minutes)
    next_minute = cs.get_next_minute()
    assert next_minute == result


@pytest.mark.parametrize(
    'hour, hours, result', [
        (1, None, 2),
        (22, None, 23),
        (23, None, None),
        (1, [5, 10], 5),
        (5, [5, 10], 10),
        (6, [5, 10], 10),
        (10, [5, 10], None),
        (11, [5, 10], None),
    ])
def test_get_next_hour(hour, hours, result):
    ls = dt(2016, 3, 27, hour=hour)
    cs = CronScheduler(last_schedule=ls, hours=hours)
    next_hour = cs.get_next_hour()
    assert next_hour == result


@pytest.mark.parametrize(
    'minutes, result', [
        (None, 0),
        ([], 0),
        ([1, 20, 40], 1),
        ([20, 40], 20),
    ])
def test_get_first_minute(minutes, result):
    cs = CronScheduler(minutes=minutes)
    assert result == cs.get_first_minute()


@pytest.mark.parametrize(
    'hours, result', [
        (None, 0),
        ([], 0),
        ([1, 10, 20], 1),
        ([10, 20], 10),
    ])
def test_get_first_hour(hours, result):
    cs = CronScheduler(hours=hours)
    assert result == cs.get_first_hour()


@pytest.mark.parametrize(
    'date, dow, dom, result', [
        (dt(2016, 3, 1), None, None, 2),
        (dt(2016, 3, 30), None, None, 31),
        (dt(2016, 3, 31), None, None, None),
        (dt(2016, 3, 7), [], [], 8),
        (dt(2016, 3, 7), [2], [], 9),
        (dt(2016, 3, 10), [2], [], 16),
        (dt(2016, 3, 10), [2, 4], [], 11),
        (dt(2016, 3, 11), [2, 4], [], 16),
        (dt(2016, 3, 16), [2, 4], [], 18),
        (dt(2016, 3, 30), [2, 4], [], None),
        (dt(2016, 3, 1), None, [13, 20], 13),
        (dt(2016, 3, 13), None, [13, 20], 20),
        (dt(2016, 3, 20), None, [13, 20], None),
        (dt(2016, 3, 10), [1, 3], [13, 20], 13),
        (dt(2016, 3, 13), [1, 3], [13, 20], 15),
        (dt(2016, 3, 15), [1, 3], [13, 20], 17),
        (dt(2016, 3, 17), [1, 3], [13, 20], 20),
        (dt(2016, 3, 20), [1, 3], [13, 20], 22),
        (dt(2016, 3, 22), [1, 3], [13, 20], 24),
        (dt(2016, 3, 24), [1, 3], [13, 20], 29),
        (dt(2016, 3, 29), [1, 3], [13, 20], 31),
        (dt(2016, 3, 31), [1, 3], [13, 20], None),
    ])
def test_get_next_day(date, dow, dom, result):
    cs = CronScheduler(last_schedule=date, dow=dow, dom=dom)
    assert result == cs.get_next_day()


@pytest.mark.parametrize(
    'date, months, result', [
        (dt(2016, 3, 27), None, (2016, 4)),
        (dt(2016, 11, 27), None, (2016, 12)),
        (dt(2016, 12, 1), None, (2017, 1)),
        (dt(2016, 3, 27), [2, 6, 11], (2016, 6)),
        (dt(2016, 6, 1), [2, 6, 11], (2016, 11)),
        (dt(2016, 11, 1), [2, 6, 11], (2017, 2)),
    ])
def test_get_next_month(date, months, result):
    cs = CronScheduler(last_schedule=date, months=months)
    assert result == cs.get_next_month()


@pytest.mark.parametrize(
    'hour, hours, result', [
        (10, None, True),
        (10, [], True),
        (10, [5, 10, 20], True),
        (11, [5, 10, 20], False),
    ])
def test_hour_is_allowed(hour, hours, result):
    date = dt(2016, 3, 27, hour)
    cs = CronScheduler(last_schedule=date, hours=hours)
    assert result == cs.hour_is_allowed()


@pytest.mark.parametrize(
    'date, dow, dom, result', [
        (dt(2016, 3, 27), None, None, True),
        (dt(2016, 3, 27), [], [], True),
        (dt(2016, 3, 27), [0, 3], [], False),
        (dt(2016, 3, 27), [0, 3, 6], [], True),
        (dt(2016, 3, 27), [], [22], False),
        (dt(2016, 3, 27), [], [10, 22], False),
        (dt(2016, 3, 27), [], [10, 22, 27], True),
        (dt(2016, 3, 27), [0, 3], [10, 22], False),
        (dt(2016, 3, 27), [0, 3, 6], [10, 22], True),
        (dt(2016, 3, 27), [0, 3, 6], [10, 22, 27], True),
    ])
def test_day_is_allowed(date, dow, dom, result):
    cs = CronScheduler(last_schedule=date, dow=dow, dom=dom)
    assert result == cs.day_is_allowed()


@pytest.mark.parametrize(
    'month, months, result', [
        (10, None, True),
        (10, [], True),
        (10, [5, 10, 12], True),
        (11, [5, 10, 12], False),
    ])
def test_month_is_allowed(month, months, result):
    date = dt(2016, month, 27)
    cs = CronScheduler(last_schedule=date, months=months)
    assert result == cs.month_is_allowed()


@pytest.mark.parametrize(
    'year, month, dow, dom, result', [
        (2016, 6, None, None, 1),
        (2016, 6, [], [], 1),
        (2016, 6, [], [10], 10),
        (2016, 6, [], [10, 20], 10),
        (2016, 6, [0], [], 6),
        (2016, 6, [0, 1], [], 6),
        (2016, 6, [0, 1, 2], [], 1),
        (2016, 6, [4], [], 3),
        (2016, 6, [0, 4], [], 3),
        (2016, 6, [0, 4], [5, 20], 3),
        (2016, 6, [0, 1], [5, 20], 5),
    ])
def test_get_first_day(year, month, dow, dom, result):
    cs = CronScheduler(dow=dow, dom=dom)
    assert result == cs.get_first_day(year, month)


@pytest.mark.parametrize(
    'date, dow, dom, hour, minute, result', [
        (dt(2016, 3, 1), None, None, 7, 30, dt(2016, 4, 1, 7, 30)),
        (dt(2016, 3, 1), None, [10, 20], 7, 30, dt(2016, 4, 10, 7, 30)),
        (dt(2016, 3, 1), [1], [10, 20], 7, 30, dt(2016, 4, 5, 7, 30)),
    ])
def test_get_schedule_next_month(date, dow, dom, hour, minute, result):
    date = make_aware(date)
    result = make_aware(result)
    cs = CronScheduler(last_schedule=date, dow=dow, dom=dom)
    assert result == cs.get_schedule_next_month(hour=hour, minute=minute)


@pytest.mark.parametrize(
    'date, months, dow, dom, hours, result', [
        (dt(2016, 3, 1), None, None, None, None, dt(2016, 3, 2, 0, 1)),
        (dt(2016, 3, 1), None, None, None, [7, 10], dt(2016, 3, 2, 7, 1)),
        (dt(2016, 3, 1), None, None, [12], [7, 10], dt(2016, 3, 12, 7, 1)),
        (dt(2016, 3, 1), None, [0], [12], [7, 10], dt(2016, 3, 7, 7, 1)),
        (dt(2016, 3, 1), [6], [0], [12], [7, 10], dt(2016, 6, 6, 7, 1)),
    ])
def test_get_schedule_next_day(date, months, dow, dom, hours, result):
    date = make_aware(date)
    result = make_aware(result)
    cs = CronScheduler(
        last_schedule=date, months=months, dow=dow, dom=dom, hours=hours)
    assert result == cs.get_schedule_next_day(minute=1)


@pytest.mark.parametrize(
    'date, months, dow, dom, hours, result', [
        (dt(2016, 3, 1), None, None, None, None, dt(2016, 3, 1, 1)),
        (dt(2016, 3, 1, 23), None, None, None, None, dt(2016, 3, 2, 0)),
        (dt(2016, 3, 2, 0), None, None, None, None, dt(2016, 3, 2, 1)),
        (dt(2016, 3, 1, 23), None, None, None, [10], dt(2016, 3, 2, 10)),
        (dt(2016, 3, 1, 23), None, None, [7], [10], dt(2016, 3, 7, 10)),
        (dt(2016, 3, 1, 23), None, [4], [7], [10], dt(2016, 3, 4, 10)),
        (dt(2016, 3, 1, 23), [5], [4], [7], [10], dt(2016, 5, 6, 10)),
    ])
def test_get_schedule_next_hour(date, months, dow, dom, hours, result):
    date = make_aware(date)
    result = make_aware(result)
    cs = CronScheduler(
        last_schedule=date, months=months, dow=dow, dom=dom, hours=hours)
    assert result == cs.get_schedule_next_hour()


@pytest.mark.parametrize(
    'date, months, dow, dom, hours, minutes, result', [
        (dt(2016, 3, 1), None, None, None, None, None, dt(2016, 3, 1, 0, 1)),
        (dt(2016, 3, 1), None, None, None, None, [15, 30], dt(2016, 3, 1, 0, 15)),
        (dt(2016, 3, 1, 0, 15), None, None, None, None, [15, 30], dt(2016, 3, 1, 0, 30)),
        (dt(2016, 3, 1), None, None, None, [12], [15, 30], dt(2016, 3, 1, 12, 15)),
        (dt(2016, 3, 1, 23), None, None, None, [12], [15, 30], dt(2016, 3, 2, 12, 15)),
        (dt(2016, 3, 1, 23), None, None, [8], [12], [15, 30], dt(2016, 3, 8, 12, 15)),
        (dt(2016, 3, 1, 23), None, [5], [8], [12], [15, 30], dt(2016, 3, 5, 12, 15)),
        (dt(2016, 3, 1, 23), [4], [5], [8], [12], [15, 30], dt(2016, 4, 2, 12, 15)),

        (dt(2016, 3, 31, 20, 10), None, None, None, None, None, dt(2016, 3, 31, 20, 11)),
        (dt(2016, 3, 31, 20, 11), None, None, None, None, None, dt(2016, 3, 31, 20, 12)),
        (dt(2016, 3, 31, 21, 40), None, None, None, [21], [21], dt(2016, 4, 1, 21, 21)),

        (dt(2016, 3, 31, 20, 11), [1], None, [1], [7], [30], dt(2017, 1, 1, 7, 30)),
        (dt(2017, 1, 1, 7, 30), [1], None, [1], [7], [30], dt(2018, 1, 1, 7, 30)),

        # finally a test for the leap year:
        (dt(2016, 2, 28), None, None, None, None, [30], dt(2016, 2, 28, 0, 30)),
        (dt(2016, 2, 28, 23), None, None, None, None, [30], dt(2016, 2, 28, 23, 30)),
        (dt(2016, 2, 28, 23, 30), None, None, None, None, [30], dt(2016, 2, 29, 0, 30)),
        (dt(2016, 2, 29, 23, 30), None, None, None, None, [30], dt(2016, 3, 1, 0, 30)),
        (dt(2015, 2, 28, 23, 30), None, None, None, None, [30], dt(2015, 3, 1, 0, 30)),
    ])
def test_get_next_schedule(date, months, dow, dom, hours, minutes, result):
    date = make_aware(date)
    result = make_aware(result)
    cs = CronScheduler(last_schedule=date, months=months,
                       dow=dow, dom=dom, hours=hours, minutes=minutes)
    assert result == cs.get_next_schedule()
