from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.response import Response
from pyramid.view import view_config

from xbus.monitor.models.monitor import DBSession
from xbus.monitor.models.monitor import EventType

from .util import get_list
from .util import get_record
from . import view_decorators


_MODEL = 'event_type'


def _update_record(request, record):
    """Update the record using JSON data."""

    try:
        vals = request.json_body

        record.name = vals['name']
        record.description = vals['description']
        record.immediate_reply = vals.get('immediate_reply', False)

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )


@view_decorators.list(_MODEL)
def event_type_list(request):
    return get_list(EventType, request.GET)


@view_decorators.create(_MODEL)
def event_type_create(request):
    record = EventType()

    _update_record(request, record)

    DBSession.add(record)
    DBSession.flush()
    DBSession.refresh(record)

    return record.as_dict()


@view_decorators.read(_MODEL)
def event_type_read(request):
    record = get_record(request, _MODEL)
    return record.as_dict()


@view_decorators.update(_MODEL)
def event_type_update(request):
    record = get_record(request, _MODEL)
    _update_record(request, record)
    return record.as_dict()


@view_decorators.delete(_MODEL)
def event_type_delete(request):
    record = get_record(request, _MODEL)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})


@view_decorators.rel_add(_MODEL)
def event_type_rel_add(request):

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
def event_type_rel_delete(request):

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
def event_type_rel_list(request):

    record = get_record(request, _MODEL)
    rel_name = request.matchdict.get('rel')
    if rel_name == 'nodes':
        return event_type_graph(request)
    rel = record.get_mapper().get_property(rel_name)
    rel_list = getattr(record, rel_name, None)
    if rel is None or rel_list is None or not hasattr(rel_list, 'filter'):
        raise HTTPBadRequest(
            json_body={
                "error": "Relationship {} does not exist".format(rel_name)
            },
        )

    return get_list(rel.mapper, request.GET, rel_list)


@view_config(
    route_name='event_type_graph',
    renderer='json',
    http_cache=0,
)
def event_type_graph(request):

    record = get_record(request, _MODEL)
    nodes = list(record.nodes)
    res, by_id, parents_cache = {}, {}, {}

    i, loop, ref = 0, 0, 'A'
    while nodes:
        if i >= len(nodes):
            i = 0
        if loop >= len(nodes):
            raise HTTPInternalServerError(
                json_body={
                    "error": "Invalid event graph",
                    "partial_res": res,
                    "remaining_node_ids": [str(node.id) for node in nodes]
                }
            )

        node = nodes[i]
        parents = parents_cache.get(node.id)
        if parents is None:
            parents = [p.id for p in node.parents]

        loop += 1
        i += 1
        if not all(p in by_id for p in parents):
            continue

        parent_refs = []
        up_depth = 0
        for parent in parents:
            parent_ref = by_id[parent]
            parent_refs.append(parent_ref)
            parent_depth = res[parent_ref]['depth']
            if parent_depth > up_depth:
                up_depth = parent_depth

        node_dict = node.as_dict()
        node_dict['depth'] = up_depth + 1
        node_dict['parent_refs'] = parent_refs
        by_id[node.id] = ref
        res[ref] = node_dict

        del nodes[i - 1]
        loop = 0
        new_ref = ""
        ret = True
        for c in ref[::-1]:
            ordc = ord(c) + 1 if ret else ord(c)
            if ordc > ord('Z'):
                new_ref = 'A' + new_ref
                ret = True
            else:
                new_ref = chr(ordc) + new_ref
                ret = False
        ref = 'A' + new_ref if ret else new_ref

    list_res = [dict(ref=key, **val) for key, val in res.items()]
    list_res.sort(key=lambda self: self['depth'])
    return list_res


@view_decorators.rel_create(_MODEL)
def event_type_rel_create(request):

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
