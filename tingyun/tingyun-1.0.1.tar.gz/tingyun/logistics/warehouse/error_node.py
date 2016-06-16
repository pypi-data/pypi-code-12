from collections import namedtuple


_ErrorNode = namedtuple('_ErrorNode', ['error_time', 'http_status', "error_class_name", 'uri', 'thread_name',
                                       "message", 'stack_trace', 'request_params', "tracker_type", "referer"])


class ErrorNode(_ErrorNode):
    """

    """
    pass
