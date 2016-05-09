import time

class Datadog(object):

    def __init__(self, auth, app_key=None, host=None, **options):
        import datadog

        # datadog we use username in auth as api_key
        datadog.initialize(api_key=auth['username'], app_key=app_key, host_name=host, **options)

        self.client = datadog.api

    def send(self, name, value, metrics_type, tags, timestamp):

        if tags is not None:
            transformed_tags = ['%s:%s' % (k, v) for k, v in tags.iteritems()]
        else:
            transformed_tags = []

        # transform into timestamp and value tuple for datadog
        if timestamp is None:
            # use current timestamp
            timestamp = int(time.time())

        self.client.Metric.send(
            metric=name,
            points=(timestamp, value),
            tags=transformed_tags,
            type=metrics_type)
