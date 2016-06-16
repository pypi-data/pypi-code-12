"""this module define the  mongodb trace data node

"""

from collections import namedtuple
from tingyun.logistics.attribution import TimeMetric, node_start_time, node_end_time

_MONGO_NODE = namedtuple("_MONGO_NODE", ['schema', 'method', 'children', 'start_time', 'end_time', 'duration',
                                         'exclusive'])


class MongoNode(_MONGO_NODE):
    """
    """
    def time_metrics(self, root, parent):
        """
        :param root:
        :param parent:
        :return:
        """
        method = str(self.method).upper()
        name = 'GENERAL/MongoDB/NULL/All'
        yield TimeMetric(name=name, scope=root.path, duration=self.duration, exclusive=self.exclusive)

        if root.type == 'WebAction':
            name = "GENERAL/MongoDB/NULL/AllWeb"
            yield TimeMetric(name=name, scope=root.path, duration=self.duration, exclusive=self.exclusive)
        else:
            name = "GENERAL/MongoDB/NULL/AllBackgound"
            yield TimeMetric(name=name, scope=root.path, duration=self.duration, exclusive=self.exclusive)

        name = "GENERAL/MongoDB/%s/%s" % (self.schema, method)
        yield TimeMetric(name=name, scope=root.path, duration=self.duration, exclusive=self.exclusive)

        name = "MongoDB/%s/%s" % (self.schema, method)
        yield TimeMetric(name=name, scope=root.path, duration=self.duration, exclusive=self.exclusive)

        name = 'GENERAL/MongoDB/NULL/%s' % method
        yield TimeMetric(name=name, scope=root.path, duration=self.duration, exclusive=self.exclusive)

    def trace_node(self, root):
        """
        :param root:
        :return:
        """
        method = str(self.method).upper()
        schema = self.schema or 'NULL'
        params = {}
        children = []
        call_count = 1
        class_name = ""
        method_name = root.name
        root.trace_node_count += 1
        start_time = node_start_time(root, self)
        end_time = node_end_time(root, self)
        metric_name = 'MongoDB/%s/%s' % (schema, method)
        call_url = metric_name

        return [start_time, end_time, metric_name, call_url, call_count, class_name, method_name, params, children]
