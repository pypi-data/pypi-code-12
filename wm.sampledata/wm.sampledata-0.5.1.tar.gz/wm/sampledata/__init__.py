# -*- coding: utf-8 -*-
import logging

from zope.component import getUtility
from zope.interface.declarations import implements

from wm.sampledata.interfaces import ISampleDataPlugin


logger = logging.getLogger('wm.sampledata')


class PluginGroup(object):
    """useful baseclass for grouping plugins by their name
    """

    implements(ISampleDataPlugin)

    PLUGINS = []

    def generate(self, context):
        for plugin in self.PLUGINS:
            if isinstance(plugin, basestring):
                plugin = getUtility(ISampleDataPlugin, name=plugin)
                plugin.generate(context)
            else:
                plugin().generate(context)
