from rest_framework import serializers, viewsets

from .factories import serializer_factory, viewset_factory


def get_all_field_names(model):
    return [field.name for field in model._meta.get_fields()]


class Endpoint:

    base_serializer = serializers.ModelSerializer
    base_viewset = viewsets.ModelViewSet
    base_readonly_viewset = viewsets.ReadOnlyModelViewSet

    model = None
    fields = None
    serializer = None

    permission_classes = None
    filter_fields = None
    search_fields = None
    ordering_fields = None
    page_size = None
    viewset = None

    read_only = False
    include_str = True

    def __init__(self, model=None, **kwargs):
        if model is not None:
            self.model = model

        arg_names = ('fields', 'serializer', 'permission_classes', 'filter_fields', 'search_fields',
                     'viewset', 'read_only', 'include_str', 'ordering_fields', 'page_size')
        for arg_name in arg_names:
            setattr(self, arg_name, kwargs.pop(arg_name, getattr(self, arg_name, None)))

        if len(kwargs.keys()) > 0:
            raise Exception('{} got an unexpected keyword argument: "{}"'.format(
                self.__class__.__name__,
                kwargs.keys()[0]
            ))

        if self.serializer is not None:
            assert self.fields is None, 'You cannot specify both fields and serializer'
        else:
            assert self.viewset is not None or self.model is not None, \
                'You need to specify at least a model or a viewset'
            self.get_serializer()

        if self.viewset is not None:
            for attr in ('permission_classes', 'filter_fields', 'search_fields', 'ordering_fields',
                         'page_size'):
                assert getattr(self, attr, None) is None, \
                    'You cannot specify both {} and viewset'.format(attr)
        else:
            self.get_viewset()

        if self.model is None:
            self.model = self.get_serializer().Meta.model

    @property
    def model_name(self):
        return self.model._meta.verbose_name_plural.lower()

    @property
    def application_name(self):
        return self.model._meta.app_label.lower()

    def get_fields(self):

        if self.fields is None:
            self.fields = tuple(get_all_field_names(self.model))
            if self.include_str:
                self.fields += ('__str__', )

        return self.fields

    def get_serializer(self):

        if self.serializer is None:
            if self.viewset is None:
                self.serializer = serializer_factory(self)
            else:
                self.serializer = self.viewset.serializer_class

        return self.serializer

    def get_base_viewset(self):
        return self.base_viewset if not self.read_only else self.base_readonly_viewset

    def get_viewset(self):

        if self.viewset is None:
            self.viewset = viewset_factory(self)

        return self.viewset

    def get_url(self):

        return '{}/{}'.format(
            self.application_name,
            self.model_name
        )
