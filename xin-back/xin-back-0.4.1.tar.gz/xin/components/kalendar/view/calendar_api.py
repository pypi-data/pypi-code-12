from ..model import Calendar

event_calendar_creation = "calendar.created"


def create_calendar(name, users=None):
    if not users:
        # todo call auth module to get the current user
        users = ['test@test.com']
    calendar = Calendar(name=name, users=users)
    calendar.commit()
    return calendar


def list_calendar(page=1, per_page=20):
    skip = (page - 1) * per_page
    calendars = Calendar.find(skip=skip, limit=per_page)
    return calendars


def get_calendar(calendar_id):
    calendar = Calendar.find_one(calendar_id)
    return calendar


def modify_calendar(calendar_id, name=None, users=None, append=False):
    errors = {}
    if not isinstance(append, bool):
        errors['append'] = 'Must be boolean'
    if name is not None and (not isinstance(name, str) or len(name) > 255):
        errors['name'] = 'Must be string or empty'
    if users is not None and not isinstance(users, list):
        errors['users'] = 'Must be list or empty'

    if users:
        if [u for u in users if not isinstance(u, str) or len(u) > 255]:
            errors['users'] = 'List element must be strings'

    if errors:
        return None

    calendar = Calendar.find_one(calendar_id)
    if not calendar:
        return None
    if name:
        calendar.data.name = name
    if users:
        if append:
            calendar.data.users.extend(users)
        else:
            calendar.data.users = users
    calendar.commit()
    return calendar


def remove_user(calendar_id, user):
    calendar = Calendar.find_one(calendar_id)
    if not calendar:
        return None
    if user in calendar.data.users:
        calendar.data.users.remove(user)
        calendar.commit()
    return calendar


def add_user(calendar_id, user):
    calendar = Calendar.find_one(calendar_id)
    if not calendar:
        return None
    if user in calendar.data.users:
        return calendar
    calendar.data.users.append(user)
    calendar.commit()
    return calendar
