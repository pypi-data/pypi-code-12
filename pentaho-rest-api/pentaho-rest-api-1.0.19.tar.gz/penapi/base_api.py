
class PentahoBaseAPI(object):

    def __init__(self, pentaho):
        if not pentaho:
            raise ValueError("[ERROR] Pentaho object is missing ... ")
        self._pentaho = pentaho
