from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response

from xbus.broker.model.auth.helpers import gen_password
from xbus.monitor.models.monitor import DBSession
from xbus.monitor.models.monitor import Emitter

from .util import get_list
from .util import get_record
from . import view_decorators


_MODEL = 'emitter'


def _update_record(request, record):
    """Update the record using JSON data."""

    try:
        vals = request.json_body

        record.login = vals['login']
        record.profile_id = vals['profile_id']

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )


@view_decorators.list(_MODEL)
def emitter_list(request):
    def wrapper(ev):
        """a small wrapper to add the profile_name key to the resulting
        records of the list
        """
        ret = ev.as_dict()
        ret['profile_name'] = ev.profile.name
        return ret

    return get_list(Emitter, request.GET, record_wrapper=wrapper)


@view_decorators.create(_MODEL)
def emitter_create(request):
    record = Emitter()

    _update_record(request, record)
    record.password = gen_password(request.json_body['password'])

    DBSession.add(record)
    DBSession.flush()
    DBSession.refresh(record)

    return record.as_dict()


@view_decorators.read(_MODEL)
def emitter_read(request):
    record = get_record(request, _MODEL)
    res = record.as_dict()
    del res['password']
    return res


@view_decorators.update(_MODEL)
def emitter_update(request):
    record = get_record(request, _MODEL)
    _update_record(request, record)
    return record.as_dict()


@view_decorators.delete(_MODEL)
def emitter_delete(request):
    record = get_record(request, _MODEL)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})
