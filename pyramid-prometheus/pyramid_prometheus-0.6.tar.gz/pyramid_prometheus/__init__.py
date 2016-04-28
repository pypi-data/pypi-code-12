from time import time

from prometheus_client import start_http_server, Histogram, Counter, REGISTRY
from pyramid.tweens import EXCVIEW

_pyramid_request = Histogram('pyramid_request', 'HTTP Requests', ['method', 'status'])

_pyramid_route_slow_count = Counter('pyramid_route_slow_count', 'Slow HTTP requests by route', ['route'])
_pyramid_route_sum = Counter('pyramid_route_sum', 'Sum of time spent processing requests by route', ['route'])
_pyramid_route_count = Counter('pyramid_route_count', 'Number of requests by route', ['route'])

def tween_factory(handler, registry):
    settings = registry.settings
    slow_request_threshold = float(settings.get('prometheus.slow_request_threshold', '1'))
    ignore_initial_request_count = int(settings.get('prometheus.ignore_initial_request_count', '10'))
    request_count = []

    def tween(request):
        start = time()
        status = '500'
        try:
            response = handler(request)
            status = str(response.status_int)
            return response
        finally:
            if len(request_count) < ignore_initial_request_count:
                # sigh, really want to use nonlocal and python 3 here
                request_count.append(None)
            else:
                duration = time() - start
                if request.matched_route is None:
                    route_name = ''
                else:
                    route_name = request.matched_route.name
                _pyramid_request.labels(request.method, status).observe(duration)
                _pyramid_route_count.labels(route_name).inc()
                _pyramid_route_sum.labels(route_name).inc(duration)
                if duration > slow_request_threshold:
                    _pyramid_route_slow_count.labels(route_name).inc()
    return tween


def includeme(config):
    settings = config.registry.settings
    port = settings.get('prometheus.port', None)
    if port:
        # if you don't specify port, you have to expose the metrics yourself somehow
        start_http_server(int(port))
    config.add_tween('pyramid_prometheus.tween_factory', over=EXCVIEW)
