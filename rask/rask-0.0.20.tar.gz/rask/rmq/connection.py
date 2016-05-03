from pika import URLParameters
from pika.adapters import TornadoConnection

__all__ = ['connection']

def connection(url,future,on_backpressure=None,on_blocked=None,on_close=None,on_error=None,on_unblocked=None):
    def on_conn(conn):
        conn.add_backpressure_callback(on_backpressure)
        conn.add_on_close_callback(on_close)
        conn.add_on_connection_blocked_callback(on_blocked)
        conn.add_on_connection_unblocked_callback(on_unblocked)
        future.set_result(conn)
        return True
    
    return TornadoConnection(
        URLParameters(url),
        on_error_callback=on_error,
        on_open_callback=on_conn,
        stop_ioloop_on_close=False
    )
