from rancon.tools import tag_replace

from dotmap import DotMap


class Service(DotMap):

    def __init__(self, name, host, port, source, **kwargs):
        super().__init__()
        self.name = name
        self.host = host
        self.port = port
        self.source = source
        for k, v in kwargs.items():
            if k not in ('host', 'port', 'source', ''):
                self[k] = v
        # perform tag replacement on all values. do three rounds so we can be
        # sure that this is working somewhat recursively
        replaced = 1
        rounds = 0
        while replaced > 0 and rounds < 3:
            replaced = 0
            rounds += 1
            for k in list(self.keys()):
                v = self[k]
                if isinstance(v, str) and v.find("%") > -1:
                    self[k] = tag_replace(v, self)
                    replaced += 1

    def __str__(self):
        return "{} ({}:{})".format(
            self.name, self.host, self.port
        )
