from __future__ import unicode_literals

__author__ = 'Meredydd Luff <meredydd@anvil.works>'

class LiveObject(object):
    def __init__(self, spec):
        self._spec = spec

    def __repr__(self):
        return "<LiveObject: " + self._spec["backend"] + ">"

class Media:
    def __getattr__(self, item):
        if item == "content":
            return self.get_content()
        elif item == "url":
            return self.get_url()
        elif item == "content_type":
            return self.get_content_type()
        else:
            raise AttributeError


class DataMedia(Media):
    def __init__(self, content_type, content):
        self._content_type = content_type
        self._content = content

    def get_content_type(self):
        return self._content_type

    def get_content(self):
        return self._content

    def get_url(self):
        raise Exception('Not yet implemented: Cannot get URLs from Media objects on the server')

    def __repr__(self):
        return "DataMedia[%s,%d bytes]" % (self._content_type, len(self._content))


def URLMedia(url):
    import anvil.server

    return anvil.server.call("anvil.private.http.request", url=url)


def is_server_side():
    return True
