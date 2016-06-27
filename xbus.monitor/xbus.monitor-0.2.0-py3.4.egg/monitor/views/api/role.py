from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response

from xbus.broker.model.auth.helpers import gen_password
from xbus.monitor.models.monitor import DBSession
from xbus.monitor.models.monitor import Role

from .util import get_list
from .util import get_record
from . import view_decorators


_MODEL = 'role'


def _update_record(request, record):
    """Update the record using JSON data."""

    try:
        vals = request.json_body

        print(vals)

        record.login = vals['login']
        record.service_id = vals['service_id']

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )


@view_decorators.list(_MODEL)
def role_list(request):
    def wrapper(ev):
        """a small wrapper to add the service_name key to the resulting
        records of the list
        """
        ret = ev.as_dict()
        ret['service_name'] = ev.service.name
        return ret

    return get_list(Role, request.GET, record_wrapper=wrapper)


@view_decorators.create(_MODEL)
def role_create(request):
    record = Role()

    _update_record(request, record)
    record.password = gen_password(request.json_body['password'])

    DBSession.add(record)
    DBSession.flush()
    DBSession.refresh(record)

    return record.as_dict()


@view_decorators.read(_MODEL)
def role_read(request):
    record = get_record(request, _MODEL)
    res = record.as_dict()
    del res['password']
    return res


@view_decorators.update(_MODEL)
def role_update(request):
    record = get_record(request, _MODEL)
    _update_record(request, record)
    return record.as_dict()


@view_decorators.delete(_MODEL)
def role_delete(request):
    record = get_record(request, _MODEL)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})
