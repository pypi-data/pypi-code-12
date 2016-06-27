from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response

from xbus.monitor.models.data_clearing import EventType
from xbus.monitor.models.data_clearing import get_session

from .util import get_list
from .util import get_record
from . import view_decorators


_MODEL = 'cl_event_type'


def _update_record(request, record):
    """Update the record using JSON data."""

    try:
        vals = request.json_body

        record.name = vals['name']
        if vals['crud_op']:
            record.crud_op = vals['crud_op']
        record.has_lookup = vals.get('has_lookup', False)
        record.has_clearing = vals.get('has_clearing', False)
        record.target_collection = vals['target_collection']
        record.test_changes = vals.get('test_changes', False)

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )


@view_decorators.list(_MODEL)
def cl_event_type_list(request):
    return get_list(EventType, request.GET, sqla_session=get_session(request))


@view_decorators.create(_MODEL)
def cl_event_type_create(request):

    record = EventType()

    _update_record(request, record)

    session = get_session(request)

    session.add(record)
    session.flush()
    session.refresh(record)

    return record.as_dict()


@view_decorators.read(_MODEL)
def cl_event_type_read(request):
    record = get_record(request, _MODEL)
    return record.as_dict()


@view_decorators.update(_MODEL)
def cl_event_type_update(request):
    record = get_record(request, _MODEL)
    _update_record(request, record)
    return record.as_dict()


@view_decorators.delete(_MODEL)
def cl_event_type_delete(request):
    record = get_record(request, _MODEL)
    get_session(request).delete(record)

    return Response(status_int=204, json_body={})


@view_decorators.rel_add(_MODEL)
def cl_event_type_rel_add(request):

    record = get_record(request, _MODEL)
    rel_name, rid = request.matchdict.get('rel'), request.matchdict.get('rid')
    rel = record.__mapper__.get_property(rel_name)
    rel_list = getattr(record, rel_name, None)
    if rel is None or rel_list is None or not hasattr(rel_list, 'append'):
        raise HTTPBadRequest(
            json_body={
                "error": "Relationship {} does not exist".format(rel_name)
            },
        )

    query = get_session(request).query(rel.mapper)
    added_record = query.get(rid)
    if added_record is None:
        raise HTTPNotFound(
            json_body={"error": "Event type ID {id} not found".format(id=rid)},
        )
    if added_record not in rel_list:
        rel_list.append(added_record)
    else:
        raise HTTPBadRequest(
            json_body={"error": "Object is already in the relationship"},
        )
    return added_record.as_dict()


@view_decorators.rel_delete(_MODEL)
def cl_event_type_rel_delete(request):

    record = get_record(request, _MODEL)
    rel_name, rid = request.matchdict.get('rel'), request.matchdict.get('rid')
    rel = record.__mapper__.get_property(rel_name)
    rel_list = getattr(record, rel_name, None)
    if rel is None or rel_list is None or not hasattr(rel_list, 'append'):
        raise HTTPBadRequest(
            json_body={
                "error": "Relationship {} does not exist".format(rel_name)
            },
        )

    query = get_session(request).query(rel.mapper)
    removed_record = query.get(rid)
    if removed_record is None:
        raise HTTPNotFound(
            json_body={"error": "Event type ID {id} not found".format(id=rid)},
        )
    if removed_record in rel_list:
        rel_list.remove(removed_record)
    else:
        raise HTTPBadRequest(
            json_body={"error": "Object is not in the relationship"},
        )
    return Response(status_int=204, json_body={})


@view_decorators.rel_list(_MODEL)
def cl_event_type_rel_list(request):

    record = get_record(request, _MODEL)
    rel_name = request.matchdict.get('rel')
    rel = record.__mapper__.get_property(rel_name)
    rel_list = getattr(record, rel_name, None)
    if rel is None or rel_list is None or not hasattr(rel_list, 'filter'):
        raise HTTPBadRequest(
            json_body={
                "error": "Relationship {} does not exist".format(rel_name)
            },
        )

    return get_list(
        rel.mapper, request.GET, rel_list, sqla_session=get_session(request)
    )


@view_decorators.rel_create(_MODEL)
def cl_event_type_rel_create(request):

    record = get_record(request, _MODEL)
    rel_name = request.matchdict.get('rel')
    rel = record.__mapper__.get_property(rel_name)
    rel_list = getattr(record, rel_name, None)
    if rel is None or rel_list is None or not hasattr(rel_list, 'filter'):
        raise HTTPBadRequest(
            json_body={
                "error": "Relationship {} does not exist".format(rel_name)
            },
        )

    created_record = rel.mapper.entity(**request.json_body)
    rel_list.append(created_record)
    return created_record.as_dict()
