# -*- coding: utf-8 -*-
"""
rio.parser
~~~~~~~~~~
"""

from urlparse import urlparse

def parse_netloc(netloc):
    """Parse netloc string."""
    auth, _netloc = netloc.split('@')
    sender, token = auth.split(':')
    domain, port = _netloc.split(':')
    port = int(port or 80)
    return dict(sender=sender, token=token, domain=domain, port=port)

def parse_path(path):
    """Parse path string."""
    version, project = path[1:].split('/')
    return dict(version=int(version), project=project)

def parse_dsn(dsn):
    """Parse dsn string."""
    parsed_dsn = urlparse(dsn)
    parsed_netloc = parse_netloc(parsed_dsn.netloc)
    parsed_path = parse_path(parsed_dsn.path)
    return {
        'scheme': parsed_dsn.scheme,
        'sender': parsed_netloc.get('sender'),
        'token': parsed_netloc.get('token'),
        'domain': parsed_netloc.get('domain'),
        'port': parsed_netloc.get('port'),
        'version': parsed_path.get('version'),
        'project': parsed_path.get('project'),
    }
