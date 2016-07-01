from rest_framework import filters, pagination


def serializer_factory(endpoint):

    meta_attrs = {
        'model': endpoint.model,
        'fields': endpoint.get_fields_for_serializer()
    }
    meta_parents = (object, )
    if hasattr(endpoint.base_serializer, 'Meta'):
        meta_parents = (endpoint.base_serializer.Meta, ) + meta_parents

    Meta = type('Meta', meta_parents, meta_attrs)

    cls_name = '{}Serializer'.format(endpoint.model.__name__)
    cls_attrs = {
        'Meta': Meta,
    }

    return type(cls_name, (endpoint.base_serializer, ), cls_attrs)


def viewset_factory(endpoint):

    cls_name = '{}ViewSet'.format(endpoint.model.__name__)
    cls_attrs = {
        'serializer_class': endpoint.get_serializer(),
        'queryset': endpoint.model.objects.all(),
        'endpoint': endpoint,
    }

    if endpoint.permission_classes is not None:
        cls_attrs['permission_classes'] = endpoint.permission_classes

    filter_backends = getattr(endpoint.get_base_viewset(), 'filter_backends', ())
    if filter_backends is None:
        filter_backends = []
    else:
        filter_backends = list(filter_backends)

    for filter_type, backend in (
        ('filter_fields', filters.DjangoFilterBackend),
        ('search_fields', filters.SearchFilter),
        ('ordering_fields', filters.OrderingFilter),
    ):

        if getattr(endpoint, filter_type, None) is not None:
            filter_backends.append(backend)
            cls_attrs[filter_type] = getattr(endpoint, filter_type)

    if len(filter_backends) > 0:
        cls_attrs['filter_backends'] = filter_backends

    if endpoint.page_size is not None:
        cls_attrs['page_size'] = endpoint.page_size
        cls_attrs['pagination_class'] = pagination.PageNumberPagination

    return type(cls_name, (endpoint.get_base_viewset(),), cls_attrs)
