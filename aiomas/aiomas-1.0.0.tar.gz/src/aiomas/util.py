"""
This module contains some utility functions.

"""
import asyncio
import importlib
import ssl

import arrow

__all__ = [
    'arrow_serializer',
    'async',
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


def async(coro_or_future, ignore_cancel=True, loop=None):
    """Run :func:`asyncio.async()` with *coro_or_future* and set a callback
    that instantly raises all exceptions.

    If *ignore_cancel* is left ``True``, no exception is raised if the task was
    canceled.  If you also want to raise the ``CancelledError``, set the flag
    to ``False.``.

    Return an :class:`asyncio.Task` object.

    The difference between this function and :func:`asyncio.async()` subtle,
    but important if an error is raised by the task:

    :func:`asyncio.async()` returns a future (:class:`asyncio.Task` is
    a subclass of :class:`asyncio.Future`) for the task that you created.  By
    the time that future goes out of scope, asyncio checks if someone was
    interested in its result or not.  If the result was never retrieved, the
    exception is printed to *stderr*.

    If you call it like ``asyncio.async(mytask())`` (note that we don't keep
    a reference to the future here), an exception in *mytask* will pre printed
    immediately when the task is done.  If, however, we store a reference to
    the future (``fut = asyncio.async(mytask())``), the exception only gets
    printed when ``fut`` goes out of scope.  That means if, for example, an
    :class:`~aiomas.agent.Agent` creates a task and stores it as an instance
    attribute, our system may keep running for a long time after the exception
    has occured (or even block forever) and we won't see any stacktrace.  This
    is because the reference to the task is still there and we could, in
    theory, still retrieve the exception from there.

    Since this can make debugging very hard, this method simply registers a
    callback to the future.  The callback will try to get the result from the
    future when it is done and will thus print any exceptions immediately.

    """
    task = asyncio.async(coro_or_future, loop=loop)

    def cb(f):
        if f.cancelled() and ignore_cancel:
            return
        f.result()  # Let the future raise the exception

    task.add_done_callback(cb)

    return task


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
