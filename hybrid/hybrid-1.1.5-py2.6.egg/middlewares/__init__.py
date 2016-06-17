import re

class ChooseAPPMiddleware:
    def __init__(self, *apps):
        self._apps = apps

    def __call__(self, environment, start_response):
        d = {}
        for app in reversed(self._apps):
            d.update(dict.fromkeys(app.reflect_uri(), app))

        uri = environment['PATH_INFO']
        for uri_pattern in d:
            if re.match(uri_pattern, uri):
                return d[uri_pattern](environment, start_response)
        return self._apps[0](environment, start_response)

