from rest_framework.metadata import SimpleMetadata, BaseMetadata


class AutoMetadataMixin:

    def determine_metadata(self, request, view):
        from drf_auto_endpoint.app_settings import settings

        metadata = super(AutoMetadataMixin, self).determine_metadata(request, view)
        if not hasattr(view, 'endpoint'):
            serializer_instance = view.serializer_class()
            metadata['fields'] = [
                {
                    'name': field,
                    'label': field.title(),
                    'widget': settings.WIDGET_MAPPING[serializer_instance().fields[field].__class__.__name__],
                }
                for field in view.serializer_class.Meta.fields
                if field != 'id'
            ]
            metadata.update({
                'list_display': ['__str__', ],
                'filter_fields': [],
                'search_fields': [],
                'ordering_fields': [],
                'fieldsets': [{'title': None, 'fields': [
                    field
                    for field in view.serializer_class.Meta.fields
                    if field != 'id' and field != '__str__'
                ]}]
            })
            return metadata

        for prop in ['fields', 'list_display', 'filter_fields', 'search_enabled', 'ordering_fields',
                     'needs', 'fieldsets']:
            metadata[prop] = getattr(view.endpoint, 'get_{}'.format(prop))()

        return metadata


class AutoMetadata(AutoMetadataMixin, SimpleMetadata):
    pass


class MinimalAutMetadata(AutoMetadataMixin, BaseMetadata):
    pass
