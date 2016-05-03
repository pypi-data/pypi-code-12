from pika import URLParameters
from pika.adapters import TornadoConnection

__all__ = ['connection']

def connection(url,future,on_error=None):
    return TornadoConnection(
        URLParameters(url),
        on_error_callback=on_error,
        on_open_callback=lambda c: future.set_result(c),
        stop_ioloop_on_close=False
    )
