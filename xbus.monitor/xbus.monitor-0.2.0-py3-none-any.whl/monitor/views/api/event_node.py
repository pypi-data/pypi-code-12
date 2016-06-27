from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response

from xbus.monitor.models.monitor import DBSession
from xbus.monitor.models.monitor import EventNode

from .util import get_list
from .util import get_record
from . import view_decorators


_MODEL = 'event_node'


def _update_record(request, record):
    """Update the record using JSON data."""

    try:
        vals = request.json_body

        record.service_id = vals['service_id']
        record.type_id = vals['type_id']
        record.is_start = vals.get('is_start', False)

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )


@view_decorators.list(_MODEL)
def event_node_list(request):
    def wrapper(ev):
        """a small wrapper to add the service_name & type_name keys
        to the resulting records of the list
        """
        ret = ev.as_dict()
        ret['service_name'] = ev.service.name
        ret['type_name'] = ev.type.name
        return ret

    return get_list(EventNode, request.GET, record_wrapper=wrapper)


@view_decorators.create(_MODEL)
def event_node_create(request):
    record = EventNode()

    _update_record(request, record)

    DBSession.add(record)
    DBSession.flush()
    DBSession.refresh(record)

    return record.as_dict()


@view_decorators.read(_MODEL)
def event_node_read(request):
    record = get_record(request, _MODEL)
    ret = record.as_dict()
    ret['service_name'] = record.service.name
    return ret


@view_decorators.update(_MODEL)
def event_node_update(request):
    record = get_record(request, _MODEL)
    _update_record(request, record)
    return record.as_dict()


@view_decorators.delete(_MODEL)
def event_node_delete(request):
    record = get_record(request, _MODEL)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})


@view_decorators.rel_add(_MODEL)
def event_node_rel_add(request):

    record = get_record(request, _MODEL)
    rel_name, rid = request.matchdict.get('rel'), request.matchdict.get('rid')
    rel = record.get_mapper().get_property(rel_name)
    rel_list = getattr(record, rel_name, None)
    if rel is None or rel_list is None or not hasattr(rel_list, 'append'):
        raise HTTPBadRequest(
            json_body={
                "error": "Relationship {} does not exist".format(rel_name)
            },
        )

    query = DBSession.query(rel.mapper)
    added_record = query.get(rid)
    if added_record is None:
        raise HTTPNotFound(
            json_body={"error": "Event node ID {id} not found".format(id=rid)},
        )
    if added_record not in rel_list:
        rel_list.append(added_record)
    else:
        raise HTTPBadRequest(
            json_body={"error": "Object is already in the relationship"},
        )
    return added_record.as_dict()


@view_decorators.rel_delete(_MODEL)
def event_node_rel_delete(request):

    record = get_record(request, _MODEL)
    rel_name, rid = request.matchdict.get('rel'), request.matchdict.get('rid')
    rel = record.get_mapper().get_property(rel_name)
    rel_list = getattr(record, rel_name, None)
    if rel is None or rel_list is None or not hasattr(rel_list, 'append'):
        raise HTTPBadRequest(
            json_body={
                "error": "Relationship {} does not exist".format(rel_name)
            },
        )

    query = DBSession.query(rel.mapper)
    removed_record = query.get(rid)
    if removed_record is None:
        raise HTTPNotFound(
            json_body={"error": "Event node ID {id} not found".format(id=rid)},
        )
    if removed_record in rel_list:
        rel_list.remove(removed_record)
    else:
        raise HTTPBadRequest(
            json_body={"error": "Object is not in the relationship"},
        )
    return Response(status_int=204, json_body={})


@view_decorators.rel_list(_MODEL)
def event_node_rel_list(request):

    record = get_record(request, _MODEL)
    rel_name = request.matchdict.get('rel')
    rel = record.get_mapper().get_property(rel_name)
    rel_list = getattr(record, rel_name, None)
    if rel is None or rel_list is None or not hasattr(rel_list, 'filter'):
        raise HTTPBadRequest(
            json_body={
                "error": "Relationship {} does not exist".format(rel_name)
            },
        )

    return get_list(rel.mapper, request.GET, rel_list)


@view_decorators.rel_create(_MODEL)
def event_node_rel_create(request):

    record = get_record(request, _MODEL)
    rel_name = request.matchdict.get('rel')
    rel = record.get_mapper().get_property(rel_name)
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
