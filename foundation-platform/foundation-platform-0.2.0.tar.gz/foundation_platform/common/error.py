# Base class for all foundation platform errors
#


class Error(Exception):
    """Base error class for the module """
    def __init__(self, msg):
        super(Error, self).__init__()
        self.__msg = msg

    def __str(self):
        return repr(self.__msg)
