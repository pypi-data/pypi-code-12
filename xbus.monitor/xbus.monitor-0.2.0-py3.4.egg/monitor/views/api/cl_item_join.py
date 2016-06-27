from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response

from xbus.monitor.models.data_clearing import get_session
from xbus.monitor.models.data_clearing import ItemJoin

from .util import get_list
from .util import get_record
from . import view_decorators


_MODEL = 'cl_item_join'


def _update_record(request, record):
    """Update the record using JSON data."""

    try:
        vals = request.json_body
        record.display_name = vals['display_name']
        record.type_id = vals['type_id']
        record.parent_id = vals.get('parent_id') or None
        record.left_column_name = vals['left_column_name']
        record.right_table_name = vals['right_table_name']
        record.right_column_name = vals['right_column_name']

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )


@view_decorators.list(_MODEL)
def cl_item_join_list(request):

    # TODO Remove the custom record wrapper when clients represent
    # relationships better (for now, we just include the data they are going
    # to need in the result list).

    def record_wrapper(record):
        """Include type names."""
        ret = record.as_dict()
        ret['type_name'] = record.type.display_name
        return ret

    return get_list(
        ItemJoin, request.GET, sqla_session=get_session(request),
        record_wrapper=record_wrapper,
    )


@view_decorators.create(_MODEL)
def cl_item_join_create(request):

    record = ItemJoin()

    _update_record(request, record)

    session = get_session(request)

    session.add(record)
    session.flush()
    session.refresh(record)

    return record.as_dict()


@view_decorators.read(_MODEL)
def cl_item_join_read(request):
    record = get_record(request, _MODEL)
    return record.as_dict()


@view_decorators.update(_MODEL)
def cl_item_join_update(request):
    record = get_record(request, _MODEL)
    _update_record(request, record)
    return record.as_dict()


@view_decorators.delete(_MODEL)
def cl_item_join_delete(request):
    record = get_record(request, _MODEL)
    get_session(request).delete(record)

    return Response(status_int=204, json_body={})
