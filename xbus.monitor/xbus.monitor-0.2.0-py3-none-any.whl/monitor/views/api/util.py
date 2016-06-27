import json
from pyramid.httpexceptions import HTTPNotFound


def get_list(
    sqla_model, params=None, query=None, sqla_session=None,
    record_wrapper=None
):
    """Helper to retrieve a record list, encoded with JSON.

    :param params: Query string to filter results.

    :param query: Custom SQLAlchemy query (one will be initialized using the
    "sqla_model" parameter otherwise).

    :param sqla_session: SQLAlchemy session object to use to run queries.
    Default: xbus.monitor.models.monitor.DBSession.

    :param record_wrapper: Function to dict-ify SQLAlchemy records. Defaults to
    "record.as_dict()".

    :return: [pagination-information, record-list].
    :rtype: 2-element list (0: dict, 1: list of dicts).
    """

    if query is None:
        if sqla_session is None:
            from xbus.monitor.models.monitor import DBSession
            sqla_session = DBSession
        query = sqla_session.query(sqla_model)

    # Filter settings.
    filters = {}
    filter_keys = (
        'page', 'per_page', 'total_pages', 'total_entries', 'sort_by', 'order',
    )

    # See whether results have to be filtered.
    if params is None:
        params = {}
    for key, value in params.items():

        # Special filter keys.
        if key in filter_keys:
            filters[key] = value
            continue

        if len(key) >= 3 and key[-3] == ':':
            param, op = key[:-3], key[-2:]
        elif value:
            param, op = key, 'eq'
        else:
            param, op = key, 'is'

        if hasattr(sqla_model, 'c'):
            col = sqla_model.c.get(param, None)
        else:
            col = getattr(sqla_model, param, None)
        if col is None:
            continue

        if op == 'in':
            value = json.loads(value)
            query = query.filter(col.in_(value))
        elif op == 'is':
            if value.lower() == 'true':
                query = query.filter(col != None)  # noqa
            else:
                query = query.filter(col == None)  # noqa
        elif op == 'eq':
            query = query.filter(col == value)
        elif op == 'ne':
            query = query.filter(col != value)
        elif op == 'gt':
            query = query.filter(col > (value if value else None))
        elif op == 'ge':
            query = query.filter(col >= (value if value else None))
        elif op == 'lt':
            query = query.filter(col < (value if value else None))
        elif op == 'le':
            query = query.filter(col <= (value if value else None))

    total_count = query.count()

    # Apply pagination settings.
    per_page = filters.get('per_page')
    if per_page:
        per_page = int(per_page)
        query = query.limit(per_page)
        page = filters.get('page')
        if page:
            page = int(page)
            query = query.offset((page - 1) * per_page)

    # TODO Sorting.

    if record_wrapper is None:
        record_wrapper = lambda record: record.as_dict()

    records = query.all()
    return [
        {'total_entries': total_count},
        [record_wrapper(record) for record in records]
    ]


def get_record(request, model):
    """Helper to ensure a record is available and return it (as an sqlalchemy
    object).
    """
    if request.context.record is None:
        raise HTTPNotFound(
            json_body={
                'error': '%{model} ID {id} not found'.format(
                    id=request.matchdict.get('id'),
                    model=model,
                ),
            },
        )
    return request.context.record
