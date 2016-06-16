
from collections import namedtuple
from tingyun.logistics.attribution import TimeMetric, node_start_time, node_end_time


_RedisNode = namedtuple('_RedisNode', ['command', 'children', 'start_time', 'end_time', 'duration', 'exclusive'])


class RedisNode(_RedisNode):
    """
    """
    def time_metrics(self, root, parent):
        """
        :param root:
        :param parent:
        :return:
        """
        command = str(self.command).upper()
        name = 'GENERAL/Redis/NULL/All'
        yield TimeMetric(name=name, scope=root.path, duration=self.duration, exclusive=self.exclusive)

        if root.type == 'WebAction':
            name = "GENERAL/Redis/NULL/AllWeb"
            yield TimeMetric(name=name, scope=root.path, duration=self.duration, exclusive=self.exclusive)
        else:
            name = "GENERAL/Redis/NULL/AllBackgound"
            yield TimeMetric(name=name, scope=root.path, duration=self.duration, exclusive=self.exclusive)

        name = 'Redis/NULL/%s' % command
        yield TimeMetric(name=name, scope=root.path, duration=self.duration, exclusive=self.exclusive)

        name = 'GENERAL/Redis/NULL/%s' % command
        yield TimeMetric(name=name, scope=root.path, duration=self.duration, exclusive=self.exclusive)

    def trace_node(self, root):
        """
        :param root:
        :return:
        """
        command = str(self.command).upper()
        params = {}
        children = []
        call_count = 1
        class_name = ""
        method_name = root.name
        root.trace_node_count += 1
        start_time = node_start_time(root, self)
        end_time = node_end_time(root, self)
        metric_name = 'Redis/NULL/%s' % command
        call_url = metric_name

        return [start_time, end_time, metric_name, call_url, call_count, class_name, method_name, params, children]
