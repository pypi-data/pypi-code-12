from xbus.monitor.models.monitor import EventError

from .util import get_list
from .util import get_record
from . import view_decorators


_MODEL = 'event_error'


@view_decorators.list(_MODEL)
def event_error_list(request):
    def wrapper(ev):
        """a small wrapper to add the envelope_id & role_login keys
        to the resulting records of the list
        """
        ret = ev.as_dict()
        ret['envelope_id'] = ev.envelope.id
        ret['role_login'] = ev.role.login if ev.role else None
        return ret

    return get_list(EventError, request.GET, record_wrapper=wrapper)


@view_decorators.read(_MODEL)
def event_error_read(request):
    record = get_record(request, _MODEL)
    ret = record.as_dict()

    ret.update({
        # Also include tracking items.
        'tracking': [tracker.id for tracker in record.tracking_list],

        # Also include user names for convenience.
        'user_name': (
            record.responsible.display_name if record.responsible else ''
        ),
    })

    return ret
