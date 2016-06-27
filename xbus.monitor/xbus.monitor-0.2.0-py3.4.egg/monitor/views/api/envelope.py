from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response

from xbus.monitor.models.monitor import DBSession
from xbus.monitor.models.monitor import Envelope

from .util import get_list
from .util import get_record
from . import view_decorators


_MODEL = 'envelope'


def _update_record(request, record):
    """Update the record using JSON data."""

    try:
        vals = request.json_body

        record.emitter_id = vals['emitter_id']
        record.state = vals['state']
        record.posted_date = vals['posted_date']
        record.done_date = vals['done_date']

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )


@view_decorators.list(_MODEL)
def envelope_list(request):
    def wrapper(ev):
        """a small wrapper to add the emitter_login key to the resulting
        records of the list
        """
        ret = ev.as_dict()
        ret['emitter_login'] = ev.emitter.login if ev.emitter else ''
        return ret

    return get_list(Envelope, request.GET, record_wrapper=wrapper)


@view_decorators.create(_MODEL)
def envelope_create(request):
    record = Envelope()

    _update_record(request, record)

    DBSession.add(record)
    DBSession.flush()
    DBSession.refresh(record)

    return record.as_dict()


@view_decorators.read(_MODEL)
def envelope_read(request):
    record = get_record(request, _MODEL)
    ret = record.as_dict()

    # Also include events and errors.
    ret.update({
        'errors': [error.id for error in record.error_list],
        'events': [event.id for event in record.event_list],
    })

    return ret


@view_decorators.update(_MODEL)
def envelope_update(request):
    record = get_record(request, _MODEL)
    _update_record(request, record)
    return record.as_dict()


@view_decorators.delete(_MODEL)
def envelope_delete(request):
    record = get_record(request, _MODEL)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})
