"""Utilities related to aiozmq.
"""

import re
import socket


def resolve_endpoint(endpoint):
    """aiozmq does not allow connecting to endpoints via host names, so resolve
    them beforehand...
    """

    # TODO Report the bug to aiozmq.

    # Taken from aiozmq.core._BaseTransport.
    TCP_RE = re.compile('^tcp://(.+):(\d+)|\*$')
    match = TCP_RE.match(endpoint)
    if not match:
        return endpoint

    return 'tcp://%s:%s' % (
        socket.gethostbyname(match.group(1)),
        match.group(2),
    )
