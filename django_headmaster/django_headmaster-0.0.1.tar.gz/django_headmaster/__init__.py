from django.conf import settings


class ImproperlyConfigured(Exception):
    """Django Headmaster is somehow improperly configured"""
    pass


class Middleware(object):
    static = list()

    def process_response(self, _, response):
        for (name, value) in self.static:
            response[name] = value
        return response

    def __init__(self):
        try:
            self.static = [(key, value) for (key, value) in settings.HEADMASTER['STATIC']]
        except ValueError:
            raise ImproperlyConfigured('Static headers should be a list of two-tuples')
        except NameError:
            pass
        except KeyError:
            pass
