from series.condition import AttrCondition
from series.handler import Handler
from series.get.model.release import ReleaseMonitor
from series.get.model.link import Link


class ReleaseAttr(AttrCondition[ReleaseMonitor]):

    def __init__(self, attr: str) -> None:
        super().__init__('release', attr)

R = ReleaseAttr


class LinkAttr(AttrCondition[Link]):

    def __init__(self, attr: str, target=True) -> None:
        super().__init__('link', attr, target)


L = LinkAttr


class BaseHandler(Handler):

    def __init__(self, data, interval, description, **kw):
        self._data = data
        super().__init__(interval, description, **kw)

    @property
    def _candidates(self):
        return self._data.all

    @property
    def _lock(self):
        return self._data.lock


class ReleaseHandler(BaseHandler):

    @property
    def _releases(self):
        return self._data

    def _update(self, monitor, **data):
        self._releases.update_by_id(monitor.id, **data)


class ShowHandler(BaseHandler):

    @property
    def _shows(self):
        return self._data

__all__ = ['ReleaseHandler', 'ShowHandler']
