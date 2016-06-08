import abc

# This is a base class which is to be used for all modes.
# For Example: For rest, netconf, and grpc.

class mode(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get(self,
            uri):
        return

    @abc.abstractmethod
    def post(self,
             uri,
             payload):
        return

    @abc.abstractmethod
    def delete(self,
               uri):
        return
