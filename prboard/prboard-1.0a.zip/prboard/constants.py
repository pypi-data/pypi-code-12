from functools import partial

# import prboard.filters as filters
import filters


class State(object):
    """

    """
    Open = 'open'
    Closed = 'closed'
    All = 'all'


FILTER_COMMAND_MAPPING = {
    'num': filters.PRNumberFilter,
    'title': filters.PRFilter,
    'etitle': partial(filters.PRFilter, wildcard=True),
    'labels': filters.LabelFilter
}


class Colors(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

INFO_LEVEL, WARNING_LEVEL, ERROR_LEVEL, SEVERE_LEVEL = range(4)
