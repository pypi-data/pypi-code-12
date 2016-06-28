# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>


class Document(object):
    """Represent a file"""
    def __init__(self):
        self._path_change_subscriptions = []
        self.saved = True  # managed by the history
        self.path = path


