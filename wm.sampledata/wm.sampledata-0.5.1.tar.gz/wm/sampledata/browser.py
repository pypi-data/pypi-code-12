# -*- coding: utf-8 -*-
from operator import itemgetter

from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError

from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from wm.sampledata import logger
from wm.sampledata.interfaces import ISampleDataPlugin


class SampleDataView(BrowserView):

    def listPlugins(self):
        """list all available plugins sorted by their name
        """
        plugins = []
        for name, util in getUtilitiesFor(ISampleDataPlugin):
            plugins.append(dict(name=name,
                                title=util.title,
                                description=util.description))

        return sorted(plugins, key=itemgetter('name'))

    def runPlugin(self, plugin, debug=False):
        """run a named plugin and redirect to the sampledata page again.
        show a status message that tells the user if the plugin
        could not be found, raised an error or ran successfully.
        """
        result = None
        try:
            plugin = getUtility(ISampleDataPlugin, name=plugin)
            result = plugin.generate(self.context)
            IStatusMessage(self.request).addStatusMessage(
                u"successfully ran %s" % plugin.title, 'info')
        except ComponentLookupError, e:
            IStatusMessage(self.request).addStatusMessage(
                u"could not find plugin %s" % plugin, 'error')
            logger.exception("could not find plugin %s" % plugin)

            if debug:
                raise e
        except Exception, e:
            IStatusMessage(self.request).addStatusMessage(
                u"error running %s: %s" % (plugin.title, str(e)), 'error')
            logger.exception(
                ("error running %s - try @@sampledata/run?"
                 "plugin=<plugin-name>&debug=True") % (plugin.title))

            if debug:
                raise e
        finally:
            if not debug:
                # return to listing
                self.request.response.redirect(
                    self.context.absolute_url() + '/@@' + self.__name__)
                return result
