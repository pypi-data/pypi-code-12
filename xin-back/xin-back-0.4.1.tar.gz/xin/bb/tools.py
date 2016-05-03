class PaginationError(Exception):
    pass


def list_to_pagination(schema, data, page=1, per_page=20, **kwargs):
    total = kwargs.pop('total', len(data))
    return {
        '_items': data,
        '_meta': {
            'page': page,
            'per_page': per_page,
            'total': total
        }
    }


def paginate(schema, queryset, page=1, per_page=20):
    if isinstance(queryset, (list, tuple)):
        total = len(queryset)
    else:
        total = queryset.count()
    end = page * per_page
    start = end - per_page
    errors = []
    data = []
    for e in queryset[start:end]:
        res = schema.dump(e)
        if res.errors:
            errors.append(res.errors)
        data.append(res.data)
    if errors:
        raise PaginationError(errors)
    return {
        '_items': data,
        '_meta': {
            'page': page,
            'per_page': per_page,
            'total': total
        }
    }
