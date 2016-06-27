import base64
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response

from xbus.monitor.models.monitor import DBSession
from xbus.monitor.models.monitor import InputDescriptor

from .util import get_list
from .util import get_record
from . import view_decorators


_MODEL = 'input_descriptor'


def _update_record(request, record):
    """Update the record using JSON data."""

    try:
        vals = request.json_body

        record.name = vals['name']

        descriptor = vals.get('descriptor')
        if descriptor:
            record.descriptor_mimetype, record.descriptor = descriptor
            record.descriptor = base64.b64decode(record.descriptor)

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )


@view_decorators.list(_MODEL)
def input_descriptor_list(request):
    return get_list(InputDescriptor, request.GET)


@view_decorators.create(_MODEL)
def input_descriptor_create(request):
    record = InputDescriptor()

    _update_record(request, record)

    DBSession.add(record)
    DBSession.flush()
    DBSession.refresh(record)

    return record.as_dict()


@view_decorators.read(_MODEL)
def input_descriptor_read(request):
    record = get_record(request, _MODEL)
    return record.as_dict()


@view_decorators.update(_MODEL)
def input_descriptor_update(request):
    record = get_record(request, _MODEL)
    _update_record(request, record)
    return record.as_dict()


@view_decorators.delete(_MODEL)
def input_descriptor_delete(request):
    record = get_record(request, _MODEL)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})
