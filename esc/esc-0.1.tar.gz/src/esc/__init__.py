import inspect

from esc.normalizers.requests import Response as RequestsResponse

DEFAULT_NORMALIZERS = (
    (("requests.models", "Response"), RequestsResponse),
)

class ESC(object):
    def __init__(self, response_normalizers={}):
        self._response_normalizers = dict(response_normalizers)

    def expect(self, status_codes, response):
        try:
            status_codes = set(status_codes)
        except TypeError:
            status_codes = {status_codes}

        normalized = self._normalize(response)
        if normalized.status_code in status_codes:
            return response

        raise self.UnexpectedStatusCode("Expected one of HTTP {}, but {} returned {} with content: {}".format(
            ", ".join(str(status_code) for status_code in status_codes),
            normalized.url,
            normalized.status_code,
            normalized.content
        ))

    def _normalize(self, response):
        """
        Given `response`, return a normalized response object that provides
        `status_code` and `text` properties.

        Normalizers are stored in `_response_normalizers`, and keyed by
        a (module, class_name) tuple. This allows us to lookup by class without
        requiring installation of each supported library.
        """

        for cls in self._iter_class_and_ancestor_classes(type(response)):
            try:
                normalizer = self._response_normalizers[(cls.__module__, cls.__name__)]
            except KeyError:
                pass
            else:
                return normalizer(response)

        raise TypeError("No normalizer found for {}".format(type(response)))

    def _iter_class_and_ancestor_classes(self, cls):
        if not inspect.isclass(cls) or not issubclass(cls, object):
            raise TypeError("Expected a class")

        yield cls

        for base in cls.__bases__:
            for ancestor in self._iter_class_and_ancestor_classes(base):
                yield ancestor

class UnexpectedStatusCode(Exception):
    pass

ESC.UnexpectedStatusCode = UnexpectedStatusCode

esc = ESC(DEFAULT_NORMALIZERS)
expect = esc.expect
