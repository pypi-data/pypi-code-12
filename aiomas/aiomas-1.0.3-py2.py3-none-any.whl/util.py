"""
This module contains some utility functions.

"""
import asyncio
import importlib
import ssl
import warnings

import arrow

__all__ = [
    'arrow_serializer',
    'async',
    'create_task',
    'run',
    'make_ssl_client_context',
    'make_ssl_server_context',
    'obj_from_str',
]


def arrow_serializer():
    """Return a serializer for *arrow* dates.

    The return value is an argument tuple for
    :meth:`aiomas.codecs.Codec.add_serializer()`.

    """
    return arrow.Arrow, str, arrow.get


def create_task(coro_or_future, *, ignore_cancel=True, loop=None):
    """Run :func:`asyncio.ensure_future()` with *coro_or_future* and set
    a callback that instantly raises all exceptions.

    If the argument is a coroutine, a :class:`asyncio.Task` object is returned.
    If the argument is a Future, it is returned directly.

    If *ignore_cancel* is left ``True``, no exception is raised if the task was
    canceled.  If you also want to raise the ``CancelledError``, set the flag
    to ``False.``.

    The difference between this function and :func:`asyncio.ensure_future()` is
    the behavior when an exception occurs within the background task:

    Exceptions that occur within the background task are normally only raised
    when you :keyword:`await` that task.  If you start a background task that
    runs "forever", you will only see the exception when your program ends and
    you either :keyword:`await` the task or if the task object gets garbage
    collected (in which case the exception is just printed to *stderr*).

    That means that your program can crash and you won't notice it because no
    exception is actually raised or printed.  To make development and debugging
    easier, this function adds a callback to the background task that will
    re-raise all exceptions immediately.

    """
    try:
        ensure_future = asyncio.ensure_future
    except AttributeError:
        # "ensure_future()" is not available in Python 3.4.0–3.4.2
        ensure_future = asyncio.async

    task = ensure_future(coro_or_future, loop=loop)

    def cb(f):
        if f.cancelled() and ignore_cancel:
            return
        f.result()  # Let the future raise the exception

    task.add_done_callback(cb)

    return task


def async(coro_or_future, ignore_cancel=True, loop=None):
    """Deprecated alias to :func:`~aiomas.util.create_task()`."""
    warnings.warn('Deprecated.  Please use "%s" instead' %
                  create_task.__qualname__, DeprecationWarning)
    return create_task(coro_or_future, ignore_cancel=True, loop=None)


def run(until=None):
    """Run the event loop forever or until the task/future *until* is finished.

    This is an alias to asyncio's ``run_forever()`` if *until* is ``None`` and
    to ``run_until_complete()`` if not.

    """
    import asyncio
    loop = asyncio.get_event_loop()
    if until is None:
        loop.run_forever()
    else:
        return loop.run_until_complete(until)


def make_ssl_server_context(cafile, certfile, keyfile):
    """Return an :class:`ssl.SSLContext` that can be used by a server socket.

    The server will use the certificate in *certfile* and private key in
    *keyfile* (both in PEM format) to authenticate itself.

    It requires clients to also authenticate themselves.  Their certificates
    will be validated with the root CA certificate in *cafile*.

    It will use *TLS 1.2* with *ECDH+AESGCM* encryption.  ECDH keys won't be
    reused in distinct SSL sessions.  Compression is disabled.

    """
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ctx.set_ciphers('ECDH+AESGCM')
    ctx.load_cert_chain(certfile=certfile, keyfile=keyfile)
    ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.load_verify_locations(cafile=cafile)
    ctx.options |= ssl.OP_SINGLE_ECDH_USE
    ctx.options |= ssl.OP_NO_COMPRESSION
    return ctx


def make_ssl_client_context(cafile, certfile, keyfile):
    """Return an :class:`ssl.SSLContext` that can be used by a client socket.

    It uses the root CA certificate in *cafile* to validate the server's
    certificate.  It will also check the server's hostname.

    The client will use the certificate in *certfile* and private key in
    *keyfile* (both in PEM format) to authenticate itself.

    It will use *TLS 1.2* with *ECDH+AESGCM* encryption.

    """
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ctx.set_ciphers('ECDH+AESGCM')
    ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.load_verify_locations(cafile=cafile)
    ctx.check_hostname = True
    ctx.load_cert_chain(certfile=certfile, keyfile=keyfile)
    return ctx


def obj_from_str(obj_path):
    """Return the object that the string *obj_path* points to.

    The format of *obj_path* is ``mod:obj`` where *mod* is a (possibly nested)
    module name and *obj* is an ``.`` separate object path, for example::

        module:Class
        module:Class.function
        package.module:Class
        package.module:Class.function

    Raise a :exc:`ValueError` if the *obj_path* is malformed, an
    :exc:`ImportError` if the module cannot be imported or an
    :exc:`AttributeError` if an object does not exist.

    """
    try:
        mod_name, obj_names = obj_path.split(':')
    except ValueError:
        raise ValueError('Malformed object name "%s": Expected "module:object"'
                         % obj_path) from None

    obj_names = obj_names.split('.')
    obj = importlib.import_module(mod_name)
    for name in obj_names:
        obj = getattr(obj, name)

    return obj
