from source.client import Client as _Client

_client = None

def get_source():
    global _client

    if _client is None:
        _client = _Client()

    return _client
