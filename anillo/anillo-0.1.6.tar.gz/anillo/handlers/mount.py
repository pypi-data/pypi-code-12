from collections import OrderedDict

from anillo.http import NotFound


class Mount():
    def __init__(self):
        self.mounts = OrderedDict()

    def mount(self, path, handler):
        self.mounts[path] = handler

    def __call__(self, request, *args, **kwargs):
        for path in self.mounts:
            if request.uri.startswith(path):
                return self.mounts[path](request, *args, **kwargs)

        return NotFound()
