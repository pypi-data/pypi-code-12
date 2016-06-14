# -*- coding: utf-8 -*-
"""
rio.parser
~~~~~~~~~~
"""

from urlparse import urlparse

def parse_netloc(scheme, netloc):
    """Parse netloc string."""
    auth, _netloc = netloc.split('@')
    sender, token = auth.split(':')
    if ':' in _netloc:
        domain, port = _netloc.split(':')
        port = int(port)
    else:
        domain = _netloc
        if scheme == 'https':
            port = 443
        else:
            port = 80
    return dict(sender=sender, token=token, domain=domain, port=port)

def parse_path(path):
    """Parse path string."""
    version, project = path[1:].split('/')
    return dict(version=int(version), project=project)

def parse_dsn(dsn):
    """Parse dsn string."""
    parsed_dsn = urlparse(dsn)
    parsed_path = parse_path(parsed_dsn.path)
    return {
        'scheme': parsed_dsn.scheme,
        'sender': parsed_dsn.username,
        'token': parsed_dsn.password,
        'domain': parsed_dsn.hostname,
        'port': parsed_dsn.port or 80,
        'version': parsed_path.get('version'),
        'project': parsed_path.get('project'),
    }
