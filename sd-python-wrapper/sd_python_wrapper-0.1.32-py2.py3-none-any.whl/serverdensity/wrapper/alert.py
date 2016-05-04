import json

from serverdensity import Response
from serverdensity.wrapper.crud import CRUD
from serverdensity.wrapper.jsonobject import JsonObject


class Alert(JsonObject, CRUD):

    _schemapath = '/schema/alerts.json'

    PATHS = {
        'create': '/alerts/configs',
        'delete': '/alerts/configs/{}',
        'list': '/alerts/configs',
        'list_by_subject': '/alerts/configs/{}',
        'update': '/alerts/configs/{}',
        'view': '/alerts/configs/{}',
        'triggered': '/alerts/triggered',
        'device_metrics': '/alerts/device_alerts.json',
        'service_metrics': '/alerts/service_alerts.json'
    }

    def triggered(self, _id=None, subject_type=None, closed=None, **kwargs):
        kwargs.setdefault('params', {})
        kwargs['params'].setdefault('filter', {})
        if _id and subject_type:
            filter = {
                'config.subjectType': subject_type,
                'config.subjectId': _id
            }
            kwargs['params']['filter'] = filter

        if closed:
            kwargs['params'].setdefault('filter', {})['fixed'] = closed
        kwargs['params']['filter'] = json.dumps(kwargs['params']['filter'], sort_keys=True)
        result = self.api.get(url=self.PATHS['triggered'], **kwargs)
        return [Response(item) for item in result]

    def device_metrics(self, **kwargs):
        return Response(self.api.get(url=self.PATHS['device_metrics'], **kwargs))

    def service_metrics(self, **kwargs):
        return Response(self.api.get(url=self.PATHS['service_metrics'], **kwargs))
