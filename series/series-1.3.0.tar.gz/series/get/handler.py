from series.handler import Handler


class BaseHandler(Handler):

    def __init__(self, data, interval, description, **kw):
        self._data = data
        super(BaseHandler, self).__init__(interval, description, **kw)

    @property
    def _candidates(self):
        return self._data.all

    def _commit(self):
        self._data.commit()

    @property
    def _lock(self):
        return self._data.lock


class ReleaseHandler(BaseHandler):

    @property
    def _releases(self):
        return self._data


class ShowHandler(BaseHandler):

    @property
    def _shows(self):
        return self._data

__all__ = ['ReleaseHandler', 'ShowHandler']
