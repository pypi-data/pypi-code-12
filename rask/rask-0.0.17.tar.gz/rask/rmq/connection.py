from pika import URLParameters
from pika.adapters.tornado_connection import TornadoConnection

__all__ = ['connection']

def connection(url,future,connector=TornadoConnection):
    connector(
        URLParameters(url),
        on_open_callback=lambda connection: future.set_result(connection),
        stop_ioloop_on_close=False
    )
    return True
