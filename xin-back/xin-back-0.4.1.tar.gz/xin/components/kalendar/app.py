#! /usr/bin/env python3

from .view import (
    create_calendar, list_calendar, get_calendar, modify_calendar, add_user, remove_user,
    create_meeting, list_meetings, get_meeting, modify_meeting, delete_meeting)

from bson import ObjectId
import autobahn_sync


def treat_data(data):
    if not data:
        return 404, {'message', 'Not Found'}
    return 200, data.dump()


@autobahn_sync.register('kalendar.create')
def calendar_create(name, users):
    calendar = create_calendar(name, users)
    return treat_data(calendar)


@autobahn_sync.register('kalendar.list')
def calendar_list(page=1, per_page=20):
    cursor = list_calendar(page, per_page)
    calendars = [c.dump() for c in cursor]
    return 200, calendars


@autobahn_sync.register('kalendar.get')
def calendar_get(calendar_id):
    calendar = get_calendar(ObjectId(calendar_id))
    return treat_data(calendar)


@autobahn_sync.register('kalendar.modify')
def calendar_modify(calendar_id, name=None, users=None, append=False):
    calendar = modify_calendar(ObjectId(calendar_id), name, users, append)
    return treat_data(calendar)


@autobahn_sync.register('kalendar.add_user')
def calendar_add_user(calendar_id, user):
    calendar = add_user(ObjectId(calendar_id), user)
    return treat_data(calendar)


@autobahn_sync.register('kalendar.remove_user')
def calendar_remove_user(calendar_id, user):
    calendar = remove_user(ObjectId(calendar_id), user)
    return treat_data(calendar)


@autobahn_sync.register('kalendar.meeting.create')
def meeting_create(calendar_id, name, users, date_begin, duration=None,
                   place=None, comment=None, tags=None):
    meeting = create_meeting(ObjectId(calendar_id), name, users, date_begin,
                             duration, place, comment, tags)
    return treat_data(meeting)


@autobahn_sync.register('kalendar.meeting.list')
def meeting_list(calendar_id):
    return list_meetings(calendar_id)


@autobahn_sync.register('kalendar.meeting.get')
def meeting_get(meeting_id):
    meeting = get_meeting(ObjectId(meeting_id))
    return treat_data(meeting)


@autobahn_sync.register('kalendar.meeting.modify')
def meeting_modify(meeting_id, name=None, users=None, append=False, date_begin=None,
                   duration=None, place=None, comment=None, tags=None):
    meeting = modify_meeting(meeting_id, name, users, append, date_begin,
                             duration, place, comment, tags)
    return treat_data(meeting)


@autobahn_sync.register('kalendar.meeting.delete')
def meeting_delete(meeting_id):
    if delete_meeting(meeting_id):
        return 204
    return 400, {'message': 'do not succeed to delete the meeting'}


@autobahn_sync.on_challenge
def on_challenge(challenge):
    import json
    return json.dumps({'application_name': 'kalendar', 'version': 0.1})


def main():
    autobahn_sync.run(blocking=True, authid="app", authmethods=[u"ticket"])


if __name__ == '__main__':
    main()
