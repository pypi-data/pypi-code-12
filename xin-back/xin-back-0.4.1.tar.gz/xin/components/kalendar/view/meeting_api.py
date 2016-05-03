from ..model import Meeting, Calendar
from datetime import datetime

event_meeting_creation = "meeting.created"


def create_meeting(calendar_id, name, users=None, date_begin=None, duration=60,
                   place="Undefined", comment=None, tags=None):
    calendar = Calendar.find_one(calendar_id)
    if not calendar:
        return {'_errors': '404'}, 404

    if not users or not len(users):
        # todo call auth module to get the current user
        users = calendar.data.users

    if not date_begin:
        date_begin = datetime.utcnow()

    meeting = Meeting(calendar=calendar.pk, name=name, users=users,
                      tags=tags if tags else [], comment=comment if comment else "",
                      begin=date_begin, duration=duration, place=place)
    meeting.commit()
    return meeting


def list_meetings(calendar_id, page=1, per_page=20):
    skip = (page - 1) * per_page
    meetings = Meeting.find({'calendar': calendar_id}, skip=skip, limit=per_page)
    return meetings


def get_meeting(meeting_id):
    meeting = Meeting.find_one(meeting_id)
    return meeting


def modify_meeting(meeting_id, name=None, users=None, append=False, date_begin=None,
                   duration=None, place=None, comment=None, tags=None):
    meeting = Meeting.find_one(meeting_id)
    if not meeting:
        return None
    if name:
        meeting.data.name = name
    if users and len(users):
        if append:
            meeting.data.users.extend(users)
        else:
            meeting.data.users = users
    if date_begin:
        meeting.data.begin = date_begin
    if duration:
        meeting.data.duration = duration
    if place:
        meeting.data.place = place
    if comment:
        meeting.data.comment = comment
    if tags:
        meeting.data.tags = tags

    meeting.commit()
    return meeting


def delete_meeting(meeting_id):
    meeting = Meeting.find_one(meeting_id)
    if not meeting:
        return None
    # meeting.delete()
    # how to handle the delete via umongo?
    return meeting
