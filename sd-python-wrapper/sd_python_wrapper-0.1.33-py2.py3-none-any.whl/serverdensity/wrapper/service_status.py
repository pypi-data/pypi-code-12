from serverdensity.wrapper.jsonobject import JsonObject


class ServiceStatus(JsonObject):

    PATHS = {
        'overall': '/service-monitor/meta/{}',
        'location': '/service-monitor/last/{}'
    }

    def _validation(self, data):
        """Service Status has no post endpoints and need no validation"""
        pass

    def overall(self, _id, **kwargs):
        return self.__class__(self.api.get(url=self.PATHS['overall'].format(_id), **kwargs))

    def location(self, _id, **kwargs):
        result = self.api.get(url=self.PATHS['location'].format(_id), **kwargs)
        return [self.__class__(item) for item in result]
