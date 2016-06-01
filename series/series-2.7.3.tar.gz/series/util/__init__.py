import re

from tek.errors import ParseError


def domain(url):
    """ Extract the domain name out of url.
    """
    if isinstance(url, str):
        domain_match = re.match(r'https?://(?:www\.)?([^/]+)\.[^/]+', url)
        return domain_match.group(1) if domain_match else ''
    else: raise ParseError('Invalid input for domain(): {}'.format(url))


__all__ = ['domain']
