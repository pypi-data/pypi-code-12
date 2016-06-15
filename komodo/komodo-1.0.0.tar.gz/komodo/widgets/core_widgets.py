import pkg_resources

from komodo.widgets.base import Widget


class Number(Widget):
    def get_bundle(self):
        return pkg_resources.resource_stream('komodo.widgets', 'bundles/Number.js')

class StatusList(Widget):
    def get_bundle(self):
        return pkg_resources.resource_stream('komodo.widgets', 'bundles/StatusList.js')

class Graph(Widget):
    def get_bundle(self):
        return pkg_resources.resource_stream('komodo.widgets', 'bundles/Graph.js')

class Gauge(Widget):
    def get_bundle(self):
        return pkg_resources.resource_stream('komodo.widgets', 'bundles/Gauge.js')

class TimeSince(Widget):
    def get_bundle(self):
        return pkg_resources.resource_stream('komodo.widgets', 'bundles/TimeSince.js')

class Countdown(Widget):
    def get_bundle(self):
        return pkg_resources.resource_stream('komodo.widgets', 'bundles/Countdown.js')
