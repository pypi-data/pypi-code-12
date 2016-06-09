# coding: utf-8
from m3.actions import ControllerCache
from creadoc.report.actions import CreadocDataSourceActionPack

__author__ = 'damirazo'


class DataSource(object):
    guid = None
    name = None
    alias = None

    def data(self, request, context):
        raise NotImplementedError

    @property
    def url(self):
        pack = ControllerCache.find_pack(CreadocDataSourceActionPack)

        return '{}?source_guid={}'.format(
            pack.action_router.get_absolute_url(),
            self.guid,
        )
