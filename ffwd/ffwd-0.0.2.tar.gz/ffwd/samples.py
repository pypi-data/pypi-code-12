import json

METRIC = "metric"
EVENT = "event"


def resolve_json_serializer(instance, opts):
    version = opts.get('version', None)

    if version is None:
        return getattr(instance, '_version0_json')

    raise Exception('Unsupported version (' + str(version) + ")")


class Metric:
    def __init__(self, client, key, tags, opts):
        self._client = client
        self._key = key
        self._tags = tags
        self._opts = opts
        self._json = resolve_json_serializer(self, opts)

    def with_tags(self, **tags):
        t = dict(self._tags)
        t.update(tags)
        return Metric(self._client, self._key, t, self._opts)

    def send(self, value):
        self._client.send_json(self._json(value))

    def _version0_json(self, value):
        return {"type": METRIC, "key": self._key, "attributes": self._tags,
                "value": value}


class Event:
    def __init__(self, client, key, tags, opts):
        self._client = client
        self._key = key
        self._tags = tags
        self._opts = opts
        self._json = resolve_json_serializer(self, opts)

    def with_tags(self, **tags):
        t = dict(self._tags)
        t.update(tags)
        return Event(self._client, self._key, t, self._opts)

    def send(self):
        self._client.send_json(self._json())

    def _version0_json(self):
        return {"type": EVENT, "key": self._key, "attributes": self._tags}
