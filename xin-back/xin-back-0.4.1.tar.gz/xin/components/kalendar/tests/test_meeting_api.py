from datetime import datetime

from ..model.meeting import Meeting
from ..view import create_calendar
from ..view.meeting_api import (
    create_meeting, list_meetings, get_meeting, modify_meeting, event_meeting_creation)

from .common import BaseTest


def calendar_factory(name="test", users=["test@test.com"]):
    r = create_calendar("test", ["test@test.com"])
    return r


class TestMeetingAPI(BaseTest):

    def test_create_meeting(self):
        calendar = calendar_factory()
        r = create_meeting(calendar_id=calendar.pk, name="first meeting", users=["pika@chu.com"],
                           duration="90", place="ici et la bas", comment="pourquoi pas", tags=['pokemon'])
        assert r
        meeting = Meeting.find_one(r.pk)
        assert meeting.pk == r.pk

    def test_list_meeting(self):
        calendar = calendar_factory()
        r = create_meeting(calendar_id=calendar.pk, name="meeting1")
        r = create_meeting(calendar_id=calendar.pk, name="meeting2")
        r = create_meeting(calendar_id=calendar.pk, name="meeting3")
        r = create_meeting(calendar_id=calendar.pk, name="meeting4")
        r = create_meeting(calendar_id=calendar.pk, name="meeting5")
        r = list_meetings(calendar.pk)
        assert r
        assert r.count() == 5

    def test_get_meeting(self):
        calendar = calendar_factory()
        r = create_meeting(calendar_id=calendar.pk, name="meeting1")
        r = get_meeting(r.pk)
        assert r.data.name == "meeting1"

    def test_modify_meeting(self):
        calendar = calendar_factory()
        r = create_meeting(calendar_id=calendar.pk, name="meeting1")
        r = get_meeting(r.pk)
        assert r
        assert r.data.name == "meeting1"
        r = modify_meeting(r.pk, name="new_name")
        assert r
        assert r.data.name == "new_name"
        r = modify_meeting(r.pk, users=["pika@chu.com"])
        assert r
        assert len(r.data.users) == 1
        assert r.data.users[0] == "pika@chu.com"
        r = modify_meeting(r.pk, users=["tor@chu.com"], append=True)
        assert r
        assert len(r.data.users) == 2
        assert r.data.users[1] == "tor@chu.com"
        r = modify_meeting(r.pk, date_begin=datetime(2007, 12, 5, 12, 00))
        assert r
        assert r.data.begin == datetime(2007, 12, 5, 12, 00)
        r = modify_meeting(r.pk, duration=100)
        assert r
        assert r.data.duration == 100
        r = modify_meeting(r.pk, place="defined")
        assert r
        assert r.data.place == "defined"
