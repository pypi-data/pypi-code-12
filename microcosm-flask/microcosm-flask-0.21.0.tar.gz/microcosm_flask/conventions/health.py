"""
Health check convention.

Reports service health and basic information from the "/api/health" endpoint,
using HTTP 200/503 status codes to indicate healthiness.

"""
from flask import jsonify

from microcosm.api import defaults
from microcosm_flask.conventions.base import Convention
from microcosm_flask.errors import extract_error_message
from microcosm_flask.namespaces import Namespace
from microcosm_flask.operations import Operation


class HealthResult(object):
    def __init__(self, error=None):
        self.error = error

    def __nonzero__(self):
        return self.error is None

    def __bool__(self):
        return self.error is None

    def __str__(self):
        return "ok" if self.error is None else self.error

    def to_dict(self):
        return {
            "ok": bool(self),
            "message": str(self),
        }

    @classmethod
    def evaluate(cls, func, graph):
        try:
            func(graph)
            return cls()
        except Exception as error:
            return cls(extract_error_message(error))


class Health(object):
    """
    Wrapper around service health state.

    May contain zero or more "checks" which are just callables that take the
    current object graph as input.

    The overall health is OK if all checks are OK.

    """
    def __init__(self, graph):
        self.graph = graph
        self.name = graph.metadata.name
        self.checks = {}

    def to_dict(self):
        """
        Encode the name, the status of all checks, and the current overall status.

        """
        # evaluate checks
        checks = {
            key: HealthResult.evaluate(func, self.graph)
            for key, func in self.checks.items()
        }
        dct = dict(
            # return the service name helps for routing debugging
            name=self.name,
            ok=all(checks.values()),
        )
        if checks:
            dct["checks"] = {
                key: checks[key].to_dict()
                for key in sorted(checks.keys())
            }
        return dct


class HealthConvention(Convention):

    def __init__(self, graph):
        super(HealthConvention, self).__init__(graph)
        self.health = Health(graph)

    def configure_retrieve(self, ns, definition):
        @self.graph.route(ns.singleton_path, Operation.Retrieve, ns)
        def current_health():
            dct = self.health.to_dict()
            response = jsonify(dct)
            response.status_code = 200 if dct["ok"] else 503
            return response


@defaults(
    path_prefix="",
)
def configure_health(graph):
    """
    Configure the health endpoint.

    :returns: a handle to the `Health` object, allowing other components to
              manipulate health state.
    """
    ns = Namespace(
        path=graph.config.health_convention.path_prefix,
        subject=Health,
    )

    convention = HealthConvention(graph)
    convention.configure(ns, retrieve=tuple())
    return convention.health
