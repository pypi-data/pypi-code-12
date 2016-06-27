from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response

from xbus.monitor.models.monitor import DBSession
from xbus.monitor.models.monitor import Service

from .util import get_list
from .util import get_record
from . import view_decorators


_MODEL = 'service'


def _update_record(request, record):
    """Update the record using JSON data."""

    try:
        vals = request.json_body

        record.name = vals['name']
        record.is_consumer = vals.get('is_consumer', False)
        record.description = vals['description']

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )


@view_decorators.list(_MODEL)
def service_list(request):
    return get_list(Service, request.GET)


@view_decorators.create(_MODEL)
def service_create(request):
    record = Service()

    _update_record(request, record)

    DBSession.add(record)
    DBSession.flush()
    DBSession.refresh(record)

    return record.as_dict()


@view_decorators.read(_MODEL)
def service_read(request):
    record = get_record(request, _MODEL)
    return record.as_dict()


@view_decorators.update(_MODEL)
def service_update(request):
    record = get_record(request, _MODEL)
    _update_record(request, record)
    return record.as_dict()


@view_decorators.delete(_MODEL)
def service_delete(request):
    record = get_record(request, _MODEL)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})
