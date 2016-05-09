class Metrics(object):
    """A metrics client, which locates its backend from the URI
    """
    def __init__(self, metrics_uri, host=None):
        import urlparse

        from aquifer.backends import get_backend
        # parse the uri
        parsed_metrics_url = urlparse.urlparse(metrics_uri)

        # validate metrics uri is set with correct scheme, `metrics`
        metrics_url_scheme = parsed_metrics_url.scheme
        if metrics_url_scheme != 'metrics':
            raise ValueError('Metrics URI must start with metrics://, got %s' % metrics_url_scheme)

        # auth as the username:password part
        auth = {
            'username': parsed_metrics_url.username,
            'password': parsed_metrics_url.password,
        }

        parsed_options = urlparse.parse_qs(parsed_metrics_url.query)

        # parsed options is a dictionary with querystring
        # value as list (since it's legal to contain duplicate keys),
        # just take the first value
        options = {k:v_list[0] for k, v_list in parsed_options.iteritems()}

        backend_cls = get_backend(parsed_metrics_url.hostname)

        self.backend = backend_cls(auth=auth, host=host, **options)

    # send a metric
    def send(self, name, value, metrics_type='gauge', tags=None, timestamp=None):
        self.backend.send(
            name=name,
            value=value,
            metrics_type=metrics_type,
            tags=tags,
            timestamp=timestamp
        )
