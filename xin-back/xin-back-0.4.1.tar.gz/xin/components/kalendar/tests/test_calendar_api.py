from ..model.calendar_model import Calendar
from ..view import (
    create_calendar, list_calendar, get_calendar, modify_calendar, event_calendar_creation)

from .common import BaseTest


class TestCalendarAPI(BaseTest):

    def test_create_calendar(self):
        self.clean_db()
        Calendar.collection.drop()
        r = create_calendar("test", ["test@test.com"])
        assert r
        calendar = Calendar.find_one(r.pk)
        assert calendar.pk == r.pk

    def test_list_calendars(self):
        self.clean_db()
        r = create_calendar("test", ["test@test.com"])
        r = create_calendar("test2", ["test@test.com"])
        r = create_calendar("test3", ["test@test.com"])
        r = create_calendar("test4", ["test@test.com"])
        r = list_calendar()
        assert r.count() == 4

    def test_get_calendars(self):
        r = list_calendar()
        assert r
        assert r.count() == 4
        cursor = r
        for elem in cursor:
            r = elem
            break
        r = get_calendar(r.pk)
        assert r
        assert r.data.name == 'test'

    def test_modify_calendars(self):
        r = create_calendar("test", ["test@test.com"])
        assert r
        r = modify_calendar(calendar_id=r.pk, name="new_name")
        assert r
        assert r.data.name == 'new_name'
        r = modify_calendar(calendar_id=r.pk, users=["pika@chu.com"])
        assert r
        assert len(r.data.users) == 1
        assert r.data.users[0] == "pika@chu.com"
        r = modify_calendar(calendar_id=r.pk, users=["tor@tank.com"], append=True)
        assert r
        assert len(r.data.users) == 2
        assert r.data.users[0] == "pika@chu.com"
        assert r.data.users[1] == "tor@tank.com"
