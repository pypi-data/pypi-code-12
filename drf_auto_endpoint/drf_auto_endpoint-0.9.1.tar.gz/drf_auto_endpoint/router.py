from collections import OrderedDict

from rest_framework.routers import DefaultRouter

from .endpoints import Endpoint


class EndpointRouter(DefaultRouter):

    base_endpoint_class = Endpoint

    def __init__(self, *args, **kwargs):
        self._endpoints = OrderedDict()
        super(EndpointRouter, self).__init__(*args, **kwargs)

    def register(self, model=None, endpoint=None, fields=None, permission_classes=None,
                 serializer=None, filter_fields=None, read_only=False, viewset=None,
                 search_fields=None, ordering_fields=None, page_size=None, **kwargs):

        if endpoint is None:
            endpoint = self.base_endpoint_class(model=model, fields=fields,
                                                permission_classes=permission_classes,
                                                serializer=serializer, filter_fields=filter_fields,
                                                read_only=read_only, viewset=viewset,
                                                search_fields=search_fields,
                                                ordering_fields=ordering_fields)

        url = endpoint.get_url() if 'url' not in kwargs else kwargs.pop('url')
        self._endpoints[url] = endpoint
        super(EndpointRouter, self).register(
            url,
            endpoint.get_viewset(),
            **kwargs
        )

    def get_endpoint(self, url):
        return self._endpoints[url]

    def registerViewSet(self, *args, **kwargs):
        super(EndpointRouter, self).register(*args, **kwargs)


router = EndpointRouter()
